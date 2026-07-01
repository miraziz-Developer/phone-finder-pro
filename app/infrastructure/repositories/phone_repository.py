"""PostgreSQL phone repository."""

from decimal import Decimal

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.phone import Phone
from app.domain.repositories import IPhoneRepository
from app.infrastructure.postgres.mappers import map_phone
from app.infrastructure.postgres.models import PhoneModel
from app.shared.enums import PhoneSortOrder


class PhoneRepository(IPhoneRepository):
    """PostgreSQL implementation of IPhoneRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base_query(self):
        return select(PhoneModel).options(
            selectinload(PhoneModel.brand),
            selectinload(PhoneModel.category),
            selectinload(PhoneModel.features),
            selectinload(PhoneModel.images),
        )

    async def get_by_id(self, phone_id: int) -> Phone | None:
        result = await self._session.execute(self._base_query().where(PhoneModel.id == phone_id))
        model = result.scalar_one_or_none()
        return map_phone(model) if model else None

    async def get_all_active(self) -> list[Phone]:
        result = await self._session.execute(
            self._base_query().where(PhoneModel.is_active.is_(True))
        )
        return [map_phone(m) for m in result.scalars().all()]

    async def search(
        self,
        *,
        brand_id: int | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        min_ram_gb: int | None = None,
        query: str | None = None,
        sort: PhoneSortOrder = PhoneSortOrder.SCORE,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Phone]:
        stmt = self._base_query().where(PhoneModel.is_active.is_(True))

        if brand_id is not None:
            stmt = stmt.where(PhoneModel.brand_id == brand_id)
        if min_price is not None:
            stmt = stmt.where(PhoneModel.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(PhoneModel.price <= max_price)
        if min_ram_gb is not None:
            stmt = stmt.where(PhoneModel.ram_gb >= min_ram_gb)
        if query:
            pattern = f"%{query}%"
            stmt = stmt.where(or_(PhoneModel.name.ilike(pattern), PhoneModel.cpu.ilike(pattern)))

        order_map = {
            PhoneSortOrder.PRICE_ASC: PhoneModel.price.asc(),
            PhoneSortOrder.PRICE_DESC: PhoneModel.price.desc(),
            PhoneSortOrder.NEWEST: PhoneModel.model_year.desc(),
            PhoneSortOrder.POPULAR: PhoneModel.recommendation_count.desc(),
            PhoneSortOrder.SCORE: PhoneModel.performance_score.desc(),
        }
        stmt = stmt.order_by(order_map.get(sort, PhoneModel.performance_score.desc()))
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        return [map_phone(m) for m in result.scalars().all()]

    async def create(self, phone: Phone) -> Phone:
        model = PhoneModel(
            brand_id=phone.brand_id,
            category_id=phone.category_id,
            name=phone.name,
            slug=phone.slug,
            model_year=phone.model_year,
            price=phone.price,
            currency=phone.currency,
            cpu=phone.cpu,
            gpu=phone.gpu,
            ram_gb=phone.ram_gb,
            storage_gb=phone.storage_gb,
            battery_mah=phone.battery_mah,
            camera_main_mp=phone.camera_main_mp,
            camera_ultra_mp=phone.camera_ultra_mp,
            camera_tele_mp=phone.camera_tele_mp,
            camera_front_mp=phone.camera_front_mp,
            performance_score=phone.performance_score,
            camera_score=phone.camera_score,
            battery_score=phone.battery_score,
            display_score=phone.display_score,
            advantages=phone.advantages,
            disadvantages=phone.disadvantages,
            is_active=phone.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return map_phone(model, load_relations=False)

    async def update(self, phone: Phone) -> Phone:
        result = await self._session.execute(self._base_query().where(PhoneModel.id == phone.id))
        model = result.scalar_one()
        model.name = phone.name
        model.price = phone.price
        model.cpu = phone.cpu
        model.ram_gb = phone.ram_gb
        model.storage_gb = phone.storage_gb
        model.battery_mah = phone.battery_mah
        model.is_active = phone.is_active
        model.advantages = phone.advantages
        model.disadvantages = phone.disadvantages
        await self._session.flush()
        return map_phone(model)

    async def delete(self, phone_id: int) -> None:
        result = await self._session.execute(select(PhoneModel).where(PhoneModel.id == phone_id))
        model = result.scalar_one_or_none()
        if model:
            model.is_active = False
            await self._session.flush()

    async def increment_view_count(self, phone_id: int) -> None:
        await self._session.execute(
            update(PhoneModel)
            .where(PhoneModel.id == phone_id)
            .values(view_count=PhoneModel.view_count + 1)
        )

    async def get_popular(self, limit: int = 10) -> list[Phone]:
        result = await self._session.execute(
            self._base_query()
            .where(PhoneModel.is_active.is_(True))
            .order_by(PhoneModel.recommendation_count.desc())
            .limit(limit)
        )
        return [map_phone(m) for m in result.scalars().all()]

    async def get_newest(self, limit: int = 10) -> list[Phone]:
        result = await self._session.execute(
            self._base_query()
            .where(PhoneModel.is_active.is_(True))
            .order_by(PhoneModel.model_year.desc(), PhoneModel.created_at.desc())
            .limit(limit)
        )
        return [map_phone(m) for m in result.scalars().all()]

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(PhoneModel).where(PhoneModel.is_active.is_(True))
        )
        return result.scalar_one()
