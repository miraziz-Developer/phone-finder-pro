"""PostgreSQL favorite repository."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.phone import Phone
from app.domain.repositories import IFavoriteRepository
from app.infrastructure.postgres.mappers import map_phone
from app.infrastructure.postgres.models import FavoriteModel, PhoneModel


class FavoriteRepository(IFavoriteRepository):
    """PostgreSQL implementation of IFavoriteRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_id: int, phone_id: int) -> None:
        existing = await self._session.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.phone_id == phone_id,
            )
        )
        if existing.scalar_one_or_none() is None:
            self._session.add(FavoriteModel(user_id=user_id, phone_id=phone_id))
            await self._session.flush()

    async def remove(self, user_id: int, phone_id: int) -> None:
        result = await self._session.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.phone_id == phone_id,
            )
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def get_user_favorites(self, user_id: int) -> list[Phone]:
        result = await self._session.execute(
            select(PhoneModel)
            .join(FavoriteModel, FavoriteModel.phone_id == PhoneModel.id)
            .options(
                selectinload(PhoneModel.brand),
                selectinload(PhoneModel.category),
                selectinload(PhoneModel.features),
                selectinload(PhoneModel.images),
            )
            .where(FavoriteModel.user_id == user_id, PhoneModel.is_active.is_(True))
            .order_by(FavoriteModel.created_at.desc())
        )
        return [map_phone(m) for m in result.scalars().all()]

    async def is_favorite(self, user_id: int, phone_id: int) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(FavoriteModel)
            .where(FavoriteModel.user_id == user_id, FavoriteModel.phone_id == phone_id)
        )
        return result.scalar_one() > 0
