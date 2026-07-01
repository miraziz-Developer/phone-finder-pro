import argparse
import asyncio

from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.database.session import get_session_manager
from app.core.logging import get_logger, setup_logging
from app.infrastructure.postgres.models import (
    BrandModel,
    CategoryModel,
    PhoneFeatureModel,
    PhoneImageModel,
    PhoneModel,
    PhonePriceHistoryModel,
)
from scripts.seed_data import BRANDS, CATEGORIES, PHONES

logger = get_logger(__name__)


async def clear_catalog(session) -> None:
    await session.execute(delete(PhonePriceHistoryModel))
    await session.execute(delete(PhoneModel))
    await session.execute(delete(CategoryModel))
    await session.execute(delete(BrandModel))
    await session.flush()


async def _load_maps(session) -> tuple[dict[str, int], dict[str, int]]:
    brands = await session.execute(select(BrandModel))
    brand_map = {b.slug: b.id for b in brands.scalars().all()}
    categories = await session.execute(select(CategoryModel))
    category_map = {c.slug: c.id for c in categories.scalars().all()}
    return brand_map, category_map


async def _insert_phone(
    session,
    p: dict,
    brand_map: dict[str, int],
    category_map: dict[str, int],
) -> None:
    phone = PhoneModel(
        brand_id=brand_map[p["brand"]],
        category_id=category_map[p["category"]],
        name=p["name"],
        slug=p["slug"],
        model_year=p["model_year"],
        price=p["price"],
        original_price=p.get("original_price"),
        discount_percent=p.get("discount_percent"),
        currency="USD",
        description=p.get("description"),
        cpu=p["cpu"],
        gpu=p.get("gpu"),
        ram_gb=p["ram_gb"],
        storage_gb=p["storage_gb"],
        battery_mah=p["battery_mah"],
        charging_watts=p.get("charging_watts"),
        camera_main_mp=p["camera_main_mp"],
        camera_ultra_mp=p.get("camera_ultra_mp"),
        camera_tele_mp=p.get("camera_tele_mp"),
        camera_front_mp=p["camera_front_mp"],
        performance_score=p["performance_score"],
        camera_score=p["camera_score"],
        battery_score=p["battery_score"],
        display_score=p["display_score"],
        rating_avg=p.get("rating_avg", 0.0),
        review_count=p.get("review_count", 0),
        weight_grams=p.get("weight_grams"),
        dimensions=p.get("dimensions"),
        colors=p.get("colors", []),
        release_date=p.get("release_date"),
        advantages=p["advantages"],
        disadvantages=p["disadvantages"],
        is_active=True,
        view_count=p.get("view_count", 0),
        recommendation_count=p.get("recommendation_count", 0),
    )
    session.add(phone)
    await session.flush()

    feat = p["features"]
    session.add(
        PhoneFeatureModel(
            phone_id=phone.id,
            has_5g=feat["has_5g"],
            has_nfc=feat["has_nfc"],
            has_wireless_charging=feat["has_wireless_charging"],
            has_esim=feat["has_esim"],
            has_amoled=feat["has_amoled"],
            has_high_refresh=feat["has_high_refresh"],
            has_fingerprint=feat.get("has_fingerprint", True),
            refresh_rate_hz=feat["refresh_rate_hz"],
            display_type=feat.get("display_type", "AMOLED"),
            display_size_inches=feat["display_size_inches"],
            display_resolution=feat["display_resolution"],
            ip_rating=feat.get("ip_rating"),
            os_version=feat.get("os_version"),
            sim_type=feat.get("sim_type"),
            bluetooth=feat.get("bluetooth"),
            wifi=feat.get("wifi"),
            usb_type=feat.get("usb_type"),
            stereo_speakers=feat.get("stereo_speakers", False),
        )
    )

    for idx, url in enumerate(p["images"]):
        session.add(
            PhoneImageModel(
                phone_id=phone.id,
                url=url,
                is_primary=idx == 0,
                sort_order=idx,
            )
        )

    for entry in p.get("price_history", []):
        session.add(
            PhonePriceHistoryModel(
                phone_id=phone.id,
                price=entry["price"],
                original_price=entry.get("original_price"),
                discount_percent=entry.get("discount_percent"),
                currency="USD",
                changed_by="seed",
            )
        )


async def seed(*, reset: bool = False, sync: bool = False) -> None:
    setup_logging()
    get_settings()
    manager = get_session_manager()
    manager.init()

    async with manager.session_factory() as session:
        if sync:
            brand_map, category_map = await _load_maps(session)
            if not brand_map:
                logger.info("seed_sync_skipped", reason="no_brands_run_seed_first")
                await manager.close()
                return

            existing = await session.execute(select(PhoneModel.slug))
            known_slugs = set(existing.scalars().all())
            added = 0
            for p in PHONES:
                if p["slug"] in known_slugs:
                    continue
                await _insert_phone(session, p, brand_map, category_map)
                added += 1

            await session.commit()
            logger.info("seed_sync_completed", added=added, total_catalog=len(PHONES))
            await manager.close()
            return

        existing = await session.execute(select(BrandModel).limit(1))
        if existing.scalar_one_or_none() and not reset:
            logger.info("seed_skipped", reason="data_already_exists", hint="use --reset or --sync")
            await manager.close()
            return

        if reset:
            await clear_catalog(session)
            logger.info("catalog_cleared")

        brand_map: dict[str, int] = {}
        for b in BRANDS:
            model = BrandModel(
                name=b["name"],
                slug=b["slug"],
                logo_url=b.get("logo_url"),
                is_active=True,
            )
            session.add(model)
            await session.flush()
            brand_map[b["slug"]] = model.id

        category_map: dict[str, int] = {}
        for c in CATEGORIES:
            model = CategoryModel(name=c["name"], slug=c["slug"], description=c["description"])
            session.add(model)
            await session.flush()
            category_map[c["slug"]] = model.id

        for p in PHONES:
            await _insert_phone(session, p, brand_map, category_map)

        await session.commit()
        logger.info(
            "seed_completed",
            brands=len(BRANDS),
            categories=len(CATEGORIES),
            phones=len(PHONES),
        )

    await manager.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed phone catalog")
    parser.add_argument("--reset", action="store_true", help="Clear catalog and reseed")
    parser.add_argument("--sync", action="store_true", help="Add missing phones from seed data")
    args = parser.parse_args()
    asyncio.run(seed(reset=args.reset, sync=args.sync))


if __name__ == "__main__":
    main()
