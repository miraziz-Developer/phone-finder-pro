"""PostgreSQL brand repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.brand import Brand
from app.domain.repositories import IBrandRepository
from app.infrastructure.postgres.mappers import map_brand
from app.infrastructure.postgres.models import BrandModel


class BrandRepository(IBrandRepository):
    """PostgreSQL implementation of IBrandRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Brand]:
        result = await self._session.execute(
            select(BrandModel).where(BrandModel.is_active.is_(True)).order_by(BrandModel.name)
        )
        return [map_brand(m) for m in result.scalars().all()]

    async def get_by_slug(self, slug: str) -> Brand | None:
        result = await self._session.execute(select(BrandModel).where(BrandModel.slug == slug))
        model = result.scalar_one_or_none()
        return map_brand(model) if model else None

    async def get_by_id(self, brand_id: int) -> Brand | None:
        result = await self._session.execute(select(BrandModel).where(BrandModel.id == brand_id))
        model = result.scalar_one_or_none()
        return map_brand(model) if model else None
