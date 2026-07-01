from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import DatabaseSessionManager, get_session_manager
from app.core.logging import get_logger
from app.infrastructure.repositories.brand_repository import BrandRepository
from app.infrastructure.repositories.category_repository import CategoryRepository
from app.infrastructure.repositories.favorite_repository import FavoriteRepository
from app.infrastructure.repositories.phone_repository import PhoneRepository
from app.infrastructure.repositories.recommendation_repository import RecommendationRepository
from app.infrastructure.repositories.user_repository import UserRepository

logger = get_logger(__name__)


class UnitOfWork:
    def __init__(self, session_manager: DatabaseSessionManager | None = None) -> None:
        self._session_manager = session_manager or get_session_manager()
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session_manager.init()
        self._session = self._session_manager.session_factory()
        await self._session.__aenter__()

        self.users = UserRepository(self._session)
        self.phones = PhoneRepository(self._session)
        self.brands = BrandRepository(self._session)
        self.categories = CategoryRepository(self._session)
        self.recommendations = RecommendationRepository(self._session)
        self.favorites = FavoriteRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc_type is not None:
                await self._session.rollback()
                logger.warning("unit_of_work_rollback", exc_type=exc_type.__name__)
            else:
                await self._session.commit()
        finally:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
            self._session = None

    async def flush(self) -> None:
        if self._session is not None:
            await self._session.flush()

    async def rollback(self) -> None:
        if self._session is not None:
            await self._session.rollback()

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UnitOfWork session is not active")
        return self._session
