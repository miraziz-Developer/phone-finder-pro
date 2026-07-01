from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.postgres.models import (
    BrandModel,
    CategoryModel,
    PhoneFeatureModel,
    PhoneImageModel,
    PhoneModel,
    PhonePriceHistoryModel,
)


@dataclass
class ImportStats:
    imported: int = 0
    duplicates: int = 0
    skipped: int = 0
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


class AdminPhoneService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def slug_exists(self, slug: str) -> bool:
        result = await self._session.execute(select(PhoneModel.id).where(PhoneModel.slug == slug))
        return result.scalar_one_or_none() is not None

    async def _get_or_create_brand(self, slug: str) -> BrandModel:
        result = await self._session.execute(select(BrandModel).where(BrandModel.slug == slug))
        brand = result.scalar_one_or_none()
        if brand:
            return brand
        brand = BrandModel(name=slug.title(), slug=slug, is_active=True)
        self._session.add(brand)
        await self._session.flush()
        return brand

    async def _get_or_create_category(self, slug: str = "mid-range") -> CategoryModel:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.slug == slug)
        )
        category = result.scalar_one_or_none()
        if category:
            return category
        category = CategoryModel(name=slug.replace("-", " ").title(), slug=slug)
        self._session.add(category)
        await self._session.flush()
        return category

    async def add_phone(
        self,
        *,
        name: str,
        brand_slug: str,
        price: Decimal,
        specs: dict[str, Any] | None = None,
    ) -> int:
        specs = specs or {}
        slug = name.lower().replace(" ", "-")
        if await self.slug_exists(slug):
            raise ValueError(f"Phone '{name}' already exists")

        brand = await self._get_or_create_brand(brand_slug)
        category = await self._get_or_create_category(specs.get("category", "mid-range"))

        phone = PhoneModel(
            brand_id=brand.id,
            category_id=category.id,
            name=name,
            slug=slug,
            model_year=specs.get("model_year", 2025),
            price=price,
            currency="USD",
            cpu=specs.get("cpu", "Unknown"),
            ram_gb=specs.get("ram_gb", 8),
            storage_gb=specs.get("storage_gb", 128),
            battery_mah=specs.get("battery_mah", 4000),
            camera_main_mp=specs.get("camera_main_mp", 48),
            camera_front_mp=specs.get("camera_front_mp", 12),
            performance_score=specs.get("performance_score", 70),
            camera_score=specs.get("camera_score", 70),
            battery_score=specs.get("battery_score", 70),
            display_score=specs.get("display_score", 70),
            is_active=True,
        )
        self._session.add(phone)
        await self._session.flush()

        self._session.add(
            PhoneFeatureModel(
                phone_id=phone.id,
                display_size_inches=specs.get("display_size_inches", 6.5),
                display_resolution=specs.get("display_resolution", "2400x1080"),
            )
        )
        self._session.add(
            PhonePriceHistoryModel(
                phone_id=phone.id,
                price=price,
                currency="USD",
                changed_by="admin",
            )
        )
        return phone.id

    async def update_price(self, phone_id: int, price: Decimal) -> tuple[str, Decimal, Decimal]:
        result = await self._session.execute(select(PhoneModel).where(PhoneModel.id == phone_id))
        phone = result.scalar_one_or_none()
        if not phone:
            raise ValueError("Phone not found")

        old_price = phone.price
        phone.price = price
        self._session.add(
            PhonePriceHistoryModel(
                phone_id=phone_id,
                price=price,
                currency="USD",
                changed_by="admin",
            )
        )
        return phone.name, old_price, price

    async def add_image(self, phone_id: int, url: str) -> None:
        result = await self._session.execute(
            select(PhoneImageModel).where(PhoneImageModel.phone_id == phone_id)
        )
        existing = result.scalars().all()
        self._session.add(
            PhoneImageModel(
                phone_id=phone_id,
                url=url,
                is_primary=len(existing) == 0,
                sort_order=len(existing),
            )
        )

    async def import_rows(self, rows: list[dict[str, Any]]) -> ImportStats:
        stats = ImportStats()

        for row in rows:
            if await self.slug_exists(row["slug"]):
                stats.duplicates += 1
                continue

            try:
                brand = await self._get_or_create_brand(row["brand"])
                category = await self._get_or_create_category(row.get("category", "mid-range"))

                phone = PhoneModel(
                    brand_id=brand.id,
                    category_id=category.id,
                    name=row["name"],
                    slug=row["slug"],
                    model_year=row["model_year"],
                    price=row["price"],
                    currency="USD",
                    cpu=row["cpu"],
                    gpu=row.get("gpu"),
                    ram_gb=row["ram_gb"],
                    storage_gb=row["storage_gb"],
                    battery_mah=row["battery_mah"],
                    charging_watts=row.get("charging_watts"),
                    camera_main_mp=row["camera_main_mp"],
                    camera_front_mp=row["camera_front_mp"],
                    performance_score=row["performance_score"],
                    camera_score=row["camera_score"],
                    battery_score=row["battery_score"],
                    display_score=row["display_score"],
                    advantages=row["advantages"],
                    disadvantages=row["disadvantages"],
                    description=row.get("description"),
                    original_price=row.get("original_price"),
                    discount_percent=row.get("discount_percent"),
                    weight_grams=row.get("weight_grams"),
                    dimensions=row.get("dimensions"),
                    colors=row.get("colors", []),
                    is_active=True,
                )
                self._session.add(phone)
                await self._session.flush()

                self._session.add(PhoneFeatureModel(phone_id=phone.id, **row["features"]))

                if row.get("image_url"):
                    self._session.add(
                        PhoneImageModel(phone_id=phone.id, url=row["image_url"], is_primary=True)
                    )
                for idx, img_url in enumerate(row.get("images", [])):
                    self._session.add(
                        PhoneImageModel(phone_id=phone.id, url=img_url, sort_order=idx)
                    )

                self._session.add(
                    PhonePriceHistoryModel(
                        phone_id=phone.id,
                        price=row["price"],
                        currency="USD",
                        changed_by="import",
                    )
                )
                stats.imported += 1
            except Exception as exc:
                stats.skipped += 1
                stats.errors.append(f"{row['name']}: {exc}")

        return stats
