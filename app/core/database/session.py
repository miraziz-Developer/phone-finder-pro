"""Async SQLAlchemy session manager."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseSessionManager:
    """Manages async database engine and session factory lifecycle."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def init(self) -> None:
        """Initialize the async engine and session factory."""
        if self._engine is not None:
            return

        self._engine = create_async_engine(
            self._settings.postgres_dsn,
            echo=self._settings.app_debug,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        logger.info("database_engine_initialized", host=self._settings.postgres_host)

    async def close(self) -> None:
        """Dispose of the database engine."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("database_engine_disposed")

    @property
    def engine(self) -> AsyncEngine:
        """Return the async engine, initializing if needed."""
        if self._engine is None:
            self.init()
        assert self._engine is not None
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Return the session factory, initializing if needed."""
        if self._session_factory is None:
            self.init()
        assert self._session_factory is not None
        return self._session_factory

    async def session(self) -> AsyncGenerator[AsyncSession]:
        """Yield a database session with automatic cleanup."""
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


_session_manager: DatabaseSessionManager | None = None


def get_session_manager() -> DatabaseSessionManager:
    """Return the global session manager singleton."""
    global _session_manager
    if _session_manager is None:
        _session_manager = DatabaseSessionManager()
    return _session_manager
