"""Telegram bot factory and lifecycle."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.core.security.rate_limiter import RateLimiter
from app.infrastructure.redis.client import get_redis
from app.presentation.bot.middlewares import (
    DatabaseMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
)
from app.presentation.bot.routers import setup_routers

logger = get_logger(__name__)


async def create_bot(settings: Settings | None = None) -> tuple[Bot, Dispatcher]:
    """
    Create and configure the Telegram bot and dispatcher.

    Returns:
        Tuple of (Bot, Dispatcher) ready for polling.
    """
    cfg = settings or get_settings()
    redis = await get_redis(cfg)

    bot = Bot(
        token=cfg.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    rate_limiter = RateLimiter(redis, cfg)
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(RateLimitMiddleware(rate_limiter))
    dp.update.middleware(DatabaseMiddleware())

    dp.include_router(setup_routers())

    logger.info("bot_created", app_name=cfg.app_name)
    return bot, dp
