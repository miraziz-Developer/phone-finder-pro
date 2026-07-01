"""Bot middlewares."""

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.core.logging import bind_context, get_logger
from app.core.security.rate_limiter import RateLimiter
from app.shared.exceptions import RateLimitExceededError

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Log incoming updates with structured context."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        start = time.perf_counter()
        update: Update | None = data.get("event_update")
        user_id = None
        if update and update.event and hasattr(update.event, "from_user"):
            user = update.event.from_user  # type: ignore[union-attr]
            if user:
                user_id = user.id
                bind_context(user_id=user_id)

        try:
            result = await handler(event, data)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("update_processed", user_id=user_id, elapsed_ms=round(elapsed_ms, 2))
            return result
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.exception("update_failed", user_id=user_id, elapsed_ms=round(elapsed_ms, 2))
            raise


class RateLimitMiddleware(BaseMiddleware):
    """Enforce per-user rate limiting."""

    def __init__(self, rate_limiter: RateLimiter) -> None:
        self._rate_limiter = rate_limiter

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        update: Update | None = data.get("event_update")
        if update and update.event and hasattr(update.event, "from_user"):
            user = update.event.from_user  # type: ignore[union-attr]
            if user:
                try:
                    await self._rate_limiter.check(user.id)
                except RateLimitExceededError:
                    logger.warning("rate_limit_blocked", user_id=user.id)
                    return None
        return await handler(event, data)


class DatabaseMiddleware(BaseMiddleware):
    """Inject Unit of Work into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from app.core.database.unit_of_work import UnitOfWork

        async with UnitOfWork() as uow:
            data["uow"] = uow
            return await handler(event, data)
