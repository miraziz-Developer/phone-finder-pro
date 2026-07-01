"""Start and main menu router."""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.application.commands import RegisterUserCommand
from app.application.handlers import RegisterUserHandler
from app.core.database.unit_of_work import UnitOfWork
from app.presentation.bot.keyboards import main_menu_keyboard
from app.presentation.bot.texts import CANCELLED, HELP, WELCOME

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    """Handle /start command — register user and show welcome."""
    await state.clear()
    if message.from_user is None:
        return

    handler = RegisterUserHandler(uow)
    await handler.handle(
        RegisterUserCommand(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code or "en",
        )
    )

    await message.answer(WELCOME, reply_markup=main_menu_keyboard(), parse_mode="HTML")


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Help")
async def cmd_help(message: Message) -> None:
    """Show help information."""
    await message.answer(HELP, parse_mode="HTML")


@router.message(Command("cancel"))
@router.message(F.text == "❌ Cancel")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Cancel current FSM flow."""
    await state.clear()
    await message.answer(CANCELLED, reply_markup=main_menu_keyboard(), parse_mode="HTML")


@router.message(F.text == "🏠 Main Menu")
async def main_menu(message: Message, state: FSMContext) -> None:
    """Return to main menu."""
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_menu_keyboard(), parse_mode="HTML")
