"""Application entry point."""

import asyncio
import sys

from aiogram import Bot

from app.core.config import get_settings
from app.core.database.session import get_session_manager
from app.core.logging import get_logger, setup_logging
from app.infrastructure.redis.client import close_redis
from app.presentation.bot import create_bot

logger = get_logger(__name__)


async def on_startup(bot: Bot) -> None:
    """Application startup hook."""
    settings = get_settings()
    session_manager = get_session_manager()
    session_manager.init()

    me = await bot.get_me()
    logger.info(
        "application_started",
        bot_username=me.username,
        env=settings.app_env,
    )


async def on_shutdown(bot: Bot) -> None:
    """Application shutdown hook."""
    session_manager = get_session_manager()
    await session_manager.close()
    await close_redis()
    logger.info("application_stopped")


async def main() -> None:
    """Run the Telegram bot with long polling."""
    setup_logging()
    settings = get_settings()

    bot, dp = await create_bot(settings)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        logger.info("starting_polling")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


def run() -> None:
    """Synchronous entry point for poetry scripts."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("interrupted_by_user")
        sys.exit(0)


if __name__ == "__main__":
    run()
