"""Phone comparison router."""

import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.application.handlers import SearchPhonesHandler
from app.application.queries import SearchPhonesQuery
from app.application.services.compare import PhoneCompareService
from app.core.database.unit_of_work import UnitOfWork
from app.domain.entities.phone import Phone
from app.presentation.bot.keyboards import compare_picker_inline, main_menu_keyboard
from app.presentation.bot.states import CompareStates
from app.shared.constants import MESSAGE_SEPARATOR, get_max_search_results
from app.shared.enums import PhoneSortOrder

router = Router(name="compare")
_compare_service = PhoneCompareService()


async def _load_phones(uow: UnitOfWork) -> list[Phone]:
    handler = SearchPhonesHandler(uow)
    return await handler.handle(
        SearchPhonesQuery(sort=PhoneSortOrder.PRICE_ASC, limit=get_max_search_results())
    )


async def _find_phone_by_name(uow: UnitOfWork, query: str) -> Phone | None:
    name = query.strip()
    if not name:
        return None
    handler = SearchPhonesHandler(uow)
    phones = await handler.handle(SearchPhonesQuery(query=name, limit=10))
    if not phones:
        return None
    lowered = name.lower()
    for phone in phones:
        if phone.name.lower() == lowered:
            return phone
    return phones[0]


async def _send_comparison(message: Message, phone1: Phone, phone2: Phone) -> None:
    result = _compare_service.compare([phone1, phone2])
    for phone in result.phones:
        if phone.primary_image_url:
            await message.answer_photo(
                photo=phone.primary_image_url,
                caption=f"📱 <b>{phone.name}</b> — ${phone.price:,.0f}",
                parse_mode="HTML",
            )
    await message.answer(
        _compare_service.format_telegram(result),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("compare"))
async def cmd_compare(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    await state.clear()
    await state.set_state(CompareStates.selecting)
    await state.update_data(compare_first_id=None)

    phones = await _load_phones(uow)
    if len(phones) < 2:
        await message.answer(
            "Not enough phones in catalog to compare.",
            reply_markup=main_menu_keyboard(),
        )
        await state.clear()
        return

    await message.answer(
        "⚖️ <b>Compare Phones</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        "Tap the <b>first</b> phone below,\n"
        "or send: <code>iPhone 13 vs iPhone 15</code>",
        parse_mode="HTML",
        reply_markup=compare_picker_inline(phones),
    )


@router.message(CompareStates.selecting)
async def process_compare_text(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    text = (message.text or "").strip()
    parts = re.split(r"\s+vs\s+", text, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) != 2:
        phones = await _load_phones(uow)
        await message.answer(
            "Use buttons below or send two names:\n<code>iPhone 13 vs Samsung Galaxy A55</code>",
            parse_mode="HTML",
            reply_markup=compare_picker_inline(phones),
        )
        return

    phone1 = await _find_phone_by_name(uow, parts[0])
    phone2 = await _find_phone_by_name(uow, parts[1])

    if not phone1 or not phone2:
        await message.answer(
            "Could not find one or both phones. Try the buttons or check spelling.",
            parse_mode="HTML",
        )
        return

    await _send_comparison(message, phone1, phone2)
    await state.clear()


@router.callback_query(F.data == "cmp:cancel")
async def callback_compare_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message:
        await callback.message.answer("Comparison cancelled.", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("cmp:"))
async def callback_compare_pick(
    callback: CallbackQuery, state: FSMContext, uow: UnitOfWork
) -> None:
    if callback.data is None or callback.message is None:
        return

    phone_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    first_id: int | None = data.get("compare_first_id")

    if first_id is None:
        phone = await uow.phones.get_by_id(phone_id)
        if phone is None:
            await callback.answer("Phone not found")
            return

        await state.set_state(CompareStates.selecting)
        await state.update_data(compare_first_id=phone_id)
        phones = await _load_phones(uow)
        await callback.message.answer(
            f"✅ First: <b>{phone.name}</b>\n\nNow select the <b>second</b> phone:",
            parse_mode="HTML",
            reply_markup=compare_picker_inline(phones, exclude_id=phone_id),
        )
        await callback.answer()
        return

    if phone_id == first_id:
        await callback.answer("Pick a different phone")
        return

    phone1 = await uow.phones.get_by_id(first_id)
    phone2 = await uow.phones.get_by_id(phone_id)
    await state.clear()

    if phone1 and phone2:
        await _send_comparison(callback.message, phone1, phone2)
    await callback.answer("Done!")
