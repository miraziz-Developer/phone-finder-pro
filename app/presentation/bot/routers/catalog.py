"""Catalog, search, favorites, and browse routers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.application.commands import RegisterUserCommand, ToggleFavoriteCommand
from app.application.handlers import (
    GetPhoneByIdHandler,
    GetRecommendationHistoryHandler,
    GetUserFavoritesHandler,
    RegisterUserHandler,
    SearchPhonesHandler,
    ToggleFavoriteHandler,
)
from app.application.queries import (
    GetPhoneByIdQuery,
    GetRecommendationHistoryQuery,
    GetUserFavoritesQuery,
    SearchPhonesQuery,
)
from app.core.database.unit_of_work import UnitOfWork
from app.core.utils.formatting import format_currency
from app.presentation.bot.keyboards import main_menu_keyboard, phone_actions_inline, phone_list_inline
from app.presentation.bot.states import SearchStates
from app.shared.constants import MESSAGE_SEPARATOR, get_page_size
from app.shared.enums import PhoneSortOrder

router = Router(name="catalog")


async def _ensure_user(message: Message, uow: UnitOfWork) -> int | None:
    """Register user and return internal user ID."""
    if message.from_user is None:
        return None
    handler = RegisterUserHandler(uow)
    user = await handler.handle(
        RegisterUserCommand(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code or "en",
        )
    )
    return user.id


def _format_phone_list_item(phone, index: int) -> str:
    """Format a single phone for list display."""
    return (
        f"<b>{index}. {phone.name}</b>\n"
        f"   {phone.brand_name} · {format_currency(phone.price)} · "
        f"{phone.ram_gb}GB/{phone.storage_gb}GB"
    )


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext) -> None:
    """Start phone search flow."""
    await state.set_state(SearchStates.query)
    await message.answer(
        "🔍 <b>Search Phones</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        "Enter a phone name or model to search:",
        parse_mode="HTML",
    )


@router.message(SearchStates.query)
async def process_search(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    """Process search query."""
    if message.text is None:
        return
    await state.clear()

    handler = SearchPhonesHandler(uow)
    phones = await handler.handle(SearchPhonesQuery(query=message.text, limit=get_page_size()))

    if not phones:
        await message.answer(
            "No phones found matching your query.", reply_markup=main_menu_keyboard()
        )
        return

    lines = ["🔍 <b>Search Results</b>", MESSAGE_SEPARATOR]
    for i, phone in enumerate(phones, 1):
        lines.append(_format_phone_list_item(phone, i))

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=phone_list_inline(phones))


@router.message(Command("favorites"))
@router.message(F.text == "⭐ Favorites")
async def cmd_favorites(message: Message, uow: UnitOfWork) -> None:
    """Show user favorites."""
    user_id = await _ensure_user(message, uow)
    if user_id is None:
        return

    handler = GetUserFavoritesHandler(uow)
    favorites = await handler.handle(GetUserFavoritesQuery(user_id=user_id))

    if not favorites:
        await message.answer(
            "⭐ <b>Favorites</b>\nNo saved phones yet.\nBrowse recommendations to add favorites!",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
        return

    lines = ["⭐ <b>Your Favorites</b>", MESSAGE_SEPARATOR]
    for i, phone in enumerate(favorites, 1):
        lines.append(_format_phone_list_item(phone, i))

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=phone_list_inline(favorites))


@router.message(Command("popular"))
@router.message(F.text == "📊 Popular")
async def cmd_popular(message: Message, uow: UnitOfWork) -> None:
    """Show popular phones."""
    handler = SearchPhonesHandler(uow)
    phones = await handler.handle(
        SearchPhonesQuery(sort=PhoneSortOrder.POPULAR, limit=get_page_size())
    )

    lines = ["📊 <b>Popular Phones</b>", MESSAGE_SEPARATOR]
    for i, phone in enumerate(phones, 1):
        lines.append(_format_phone_list_item(phone, i))

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=phone_list_inline(phones))


@router.message(Command("newest"))
@router.message(F.text == "🆕 Newest")
async def cmd_newest(message: Message, uow: UnitOfWork) -> None:
    """Show newest phones."""
    handler = SearchPhonesHandler(uow)
    phones = await handler.handle(
        SearchPhonesQuery(sort=PhoneSortOrder.NEWEST, limit=get_page_size())
    )

    lines = ["🆕 <b>Newest Phones</b>", MESSAGE_SEPARATOR]
    for i, phone in enumerate(phones, 1):
        lines.append(_format_phone_list_item(phone, i))

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=phone_list_inline(phones))


@router.message(Command("history"))
@router.message(F.text == "📜 History")
async def cmd_history(message: Message, uow: UnitOfWork) -> None:
    """Show recommendation history."""
    user_id = await _ensure_user(message, uow)
    if user_id is None:
        return

    handler = GetRecommendationHistoryHandler(uow)
    history = await handler.handle(GetRecommendationHistoryQuery(user_id=user_id, limit=5))

    if not history:
        await message.answer(
            "📜 <b>History</b>\nNo past recommendations yet.\nTry /recommend to get started!",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
        return

    lines = ["📜 <b>Recommendation History</b>", MESSAGE_SEPARATOR]
    for rec in history:
        top = rec.results[0] if rec.results else None
        if top:
            lines.append(f"• {top.phone_name} — {top.score:.0%} match")

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=main_menu_keyboard())


@router.message(F.text == "📱 Browse Phones")
async def cmd_browse(message: Message, uow: UnitOfWork) -> None:
    """Browse all phones."""
    handler = SearchPhonesHandler(uow)
    phones = await handler.handle(SearchPhonesQuery(limit=get_page_size()))

    lines = ["📱 <b>Phone Catalog</b>", MESSAGE_SEPARATOR]
    for i, phone in enumerate(phones, 1):
        lines.append(_format_phone_list_item(phone, i))

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=phone_list_inline(phones))


@router.callback_query(F.data.startswith("phone:"))
async def callback_phone_detail(callback: CallbackQuery, uow: UnitOfWork) -> None:
    """Show phone details from inline callback."""
    if callback.data is None or callback.message is None:
        return

    phone_id = int(callback.data.split(":")[1])
    handler = GetPhoneByIdHandler(uow)
    phone = await handler.handle(GetPhoneByIdQuery(phone_id=phone_id))

    text = (
        f"📱 <b>{phone.name}</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        f"Brand: {phone.brand_name}\n"
        f"Price: {format_currency(phone.price)}\n"
        f"CPU: {phone.cpu}\n"
        f"RAM: {phone.ram_gb}GB | Storage: {phone.storage_gb}GB\n"
        f"Battery: {phone.battery_mah}mAh\n"
        f"Camera: {phone.camera_description}"
    )

    is_fav = False
    if callback.from_user:
        user_id = await _ensure_user(callback.message, uow)
        if user_id:
            is_fav = await uow.favorites.is_favorite(user_id, phone_id)

    if phone.primary_image_url:
        await callback.message.answer_photo(
            photo=phone.primary_image_url,
            caption=text,
            parse_mode="HTML",
            reply_markup=phone_actions_inline(phone_id, is_fav),
        )
    else:
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=phone_actions_inline(phone_id, is_fav),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("fav:"))
async def callback_toggle_favorite(callback: CallbackQuery, uow: UnitOfWork) -> None:
    """Toggle favorite status."""
    if callback.data is None or callback.message is None or callback.from_user is None:
        return

    phone_id = int(callback.data.split(":")[1])
    user_id = await _ensure_user(callback.message, uow)
    if user_id is None:
        return

    handler = ToggleFavoriteHandler(uow)
    is_fav = await handler.handle(ToggleFavoriteCommand(user_id=user_id, phone_id=phone_id))

    status = "added to" if is_fav else "removed from"
    await callback.answer(f"Phone {status} favorites!")
    await callback.message.edit_reply_markup(reply_markup=phone_actions_inline(phone_id, is_fav))
