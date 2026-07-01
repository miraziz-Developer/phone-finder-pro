"""PostgreSQL category repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.category import Category
from app.domain.repositories import ICategoryRepository
from app.infrastructure.postgres.mappers import map_category
from app.infrastructure.postgres.models import CategoryModel


class CategoryRepository(ICategoryRepository):
    """PostgreSQL implementation of ICategoryRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Category]:
        result = await self._session.execute(select(CategoryModel).order_by(CategoryModel.name))
        return [map_category(m) for m in result.scalars().all()]

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return map_category(model) if model else None
