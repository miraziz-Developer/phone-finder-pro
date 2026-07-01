"""Global error handler router."""

from aiogram import Router
from aiogram.types import ErrorEvent, Message

from app.core.logging import get_logger
from app.presentation.bot.keyboards import main_menu_keyboard
from app.presentation.bot.texts import ERROR_MESSAGE, RATE_LIMIT_MESSAGE
from app.shared.exceptions import AppError, RateLimitExceededError

logger = get_logger(__name__)

router = Router(name="errors")


@router.errors()
async def global_error_handler(event: ErrorEvent) -> bool:
    """Handle unhandled exceptions in bot handlers."""
    exception = event.exception
    update = event.update

    user_id = None
    if update.message and update.message.from_user:
        user_id = update.message.from_user.id
    elif update.callback_query and update.callback_query.from_user:
        user_id = update.callback_query.from_user.id

    logger.exception("bot_handler_error", user_id=user_id, error=str(exception))

    target_message: Message | None = None
    if update.message:
        target_message = update.message
    elif update.callback_query and update.callback_query.message:
        target_message = update.callback_query.message  # type: ignore[assignment]

    if target_message is None:
        return True

    if isinstance(exception, RateLimitExceededError):
        await target_message.answer(RATE_LIMIT_MESSAGE, parse_mode="HTML")
    elif isinstance(exception, AppError):
        await target_message.answer(f"⚠️ {exception.message}", parse_mode="HTML")
    else:
        await target_message.answer(
            ERROR_MESSAGE,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )

    return True
