"""Advanced search router with filters."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.application.handlers import SearchPhonesHandler
from app.application.queries import SearchPhonesQuery
from app.core.database.unit_of_work import UnitOfWork
from app.core.utils.formatting import format_currency
from app.presentation.bot.keyboards import main_menu_keyboard, pagination_inline
from app.presentation.bot.states import SearchStates
from app.shared.constants import MESSAGE_SEPARATOR, get_page_size
from app.shared.enums import PhoneSortOrder

router = Router(name="search")


@router.message(Command("filter"))
async def cmd_advanced_search(message: Message, state: FSMContext) -> None:
    """Start advanced filter search."""
    await state.set_state(SearchStates.query)
    await message.answer(
        "🔎 <b>Smart Search</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        "Enter search query or filters:\n\n"
        "<b>By name:</b> <code>Galaxy</code>\n"
        "<b>By price:</b> <code>price:300-600</code>\n"
        "<b>By RAM:</b> <code>ram:8</code>\n"
        "<b>By brand:</b> <code>brand:samsung</code>\n"
        "<b>Combined:</b> <code>brand:apple price:500-1000 ram:8</code>",
        parse_mode="HTML",
    )


def _parse_filters(text: str) -> dict:
    """Parse advanced filter syntax from user input."""
    filters: dict = {
        "query": None,
        "brand_id": None,
        "min_price": None,
        "max_price": None,
        "min_ram_gb": None,
    }
    parts = text.split()
    plain_words = []

    for part in parts:
        if part.startswith("price:"):
            price_part = part.replace("price:", "")
            if "-" in price_part:
                lo, hi = price_part.split("-", 1)
                filters["min_price"] = float(lo)
                filters["max_price"] = float(hi)
            else:
                filters["max_price"] = float(price_part)
        elif part.startswith("ram:"):
            filters["min_ram_gb"] = int(part.replace("ram:", ""))
        elif part.startswith("brand:"):
            filters["brand_slug"] = part.replace("brand:", "").lower()
        else:
            plain_words.append(part)

    if plain_words:
        filters["query"] = " ".join(plain_words)
    return filters


@router.message(SearchStates.query)
async def process_advanced_search(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    """Execute advanced search with parsed filters."""
    if not message.text:
        return

    filters = _parse_filters(message.text)
    brand_id = None
    if filters.get("brand_slug"):
        brand = await uow.brands.get_by_slug(filters["brand_slug"])
        if brand:
            brand_id = brand.id

    handler = SearchPhonesHandler(uow)
    phones = await handler.handle(
        SearchPhonesQuery(
            brand_id=brand_id,
            min_price=filters.get("min_price"),
            max_price=filters.get("max_price"),
            min_ram_gb=filters.get("min_ram_gb"),
            query=filters.get("query"),
            sort=PhoneSortOrder.PRICE_ASC,
            limit=get_page_size(),
        )
    )

    await state.clear()

    if not phones:
        await message.answer(
            "😔 No phones match your filters.\nTry broadening your search.",
            reply_markup=main_menu_keyboard(),
        )
        return

    lines = ["🔎 <b>Search Results</b>", MESSAGE_SEPARATOR]
    for i, phone in enumerate(phones, 1):
        discount = ""
        if (
            hasattr(phone, "original_price")
            and phone.original_price
            and phone.original_price > phone.price
        ):
            discount = " 🏷"
        lines.append(
            f"{i}. <b>{phone.name}</b>{discount}\n"
            f"   {phone.brand_name} · {format_currency(phone.price)} · "
            f"{phone.ram_gb}GB · {phone.cpu[:20]}"
        )

    total_pages = max(1, (len(phones) + get_page_size() - 1) // get_page_size())
    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=pagination_inline("search", 0, total_pages)
        if total_pages > 1
        else main_menu_keyboard(),
    )
