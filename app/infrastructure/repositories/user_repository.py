"""PostgreSQL user repository."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User, UserPreference
from app.domain.repositories import IUserRepository
from app.infrastructure.postgres.mappers import map_user, map_user_preference
from app.infrastructure.postgres.models import UserModel, UserPreferenceModel


class UserRepository(IUserRepository):
    """PostgreSQL implementation of IUserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        model = result.scalar_one_or_none()
        return map_user(model) if model else None

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return map_user(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_active=user.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return map_user(model)

    async def update(self, user: User) -> User:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user.id))
        model = result.scalar_one()
        model.username = user.username
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.language_code = user.language_code
        model.is_active = user.is_active
        await self._session.flush()
        return map_user(model)

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(UserModel))
        return result.scalar_one()

    async def save_preference(self, preference: UserPreference) -> UserPreference:
        model = UserPreferenceModel(
            user_id=preference.user_id,
            budget_min=preference.budget_min,
            budget_max=preference.budget_max,
            use_case=preference.use_case,
            preferred_brand=preference.preferred_brand,
            min_ram_gb=preference.min_ram_gb,
            min_storage_gb=preference.min_storage_gb,
            requires_5g=preference.requires_5g,
            requires_nfc=preference.requires_nfc,
            requires_wireless_charging=preference.requires_wireless_charging,
            requires_esim=preference.requires_esim,
            requires_amoled=preference.requires_amoled,
            requires_high_refresh=preference.requires_high_refresh,
        )
        self._session.add(model)
        await self._session.flush()
        return map_user_preference(model)
