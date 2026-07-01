"""Phone comparison router."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.application.services.compare import PhoneCompareService
from app.core.database.unit_of_work import UnitOfWork
from app.presentation.bot.keyboards import main_menu_keyboard
from app.presentation.bot.states import CompareStates
from app.shared.constants import MESSAGE_SEPARATOR

router = Router(name="compare")
_compare_service = PhoneCompareService()


@router.message(Command("compare"))
async def cmd_compare(message: Message, state: FSMContext) -> None:
    """Start phone comparison flow."""
    await state.clear()
    await state.set_state(CompareStates.selecting)
    await state.update_data(compare_ids=[])
    await message.answer(
        "⚖️ <b>Compare Phones</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        "Send two phone IDs separated by space.\n"
        "Example: <code>1 3</code>\n\n"
        "Use /phones (admin) or browse catalog to find IDs.",
        parse_mode="HTML",
    )


@router.message(CompareStates.selecting)
async def process_compare(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    """Process comparison request."""
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer(
            "Please enter exactly 2 phone IDs: <code>1 3</code>", parse_mode="HTML"
        )
        return

    try:
        id1, id2 = int(parts[0]), int(parts[1])
    except ValueError:
        await message.answer("Invalid phone IDs.")
        return

    phone1 = await uow.phones.get_by_id(id1)
    phone2 = await uow.phones.get_by_id(id2)

    if not phone1 or not phone2:
        await message.answer("One or both phones not found.")
        await state.clear()
        return

    result = _compare_service.compare([phone1, phone2])
    text = _compare_service.format_telegram(result)

    for phone in result.phones:
        if phone.primary_image_url:
            await message.answer_photo(
                photo=phone.primary_image_url,
                caption=f"📱 <b>{phone.name}</b> — ${phone.price:,.0f}",
                parse_mode="HTML",
            )

    await message.answer(text, parse_mode="HTML", reply_markup=main_menu_keyboard())
    await state.clear()


@router.callback_query(F.data.startswith("compare:"))
async def callback_compare(callback: CallbackQuery, state: FSMContext, uow: UnitOfWork) -> None:
    """Add phone to comparison from inline button."""
    if callback.data is None:
        return
    phone_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    ids: list[int] = data.get("compare_ids", [])

    if phone_id in ids:
        await callback.answer("Already selected!")
        return

    ids.append(phone_id)
    await state.update_data(compare_ids=ids)

    if len(ids) == 2:
        phone1 = await uow.phones.get_by_id(ids[0])
        phone2 = await uow.phones.get_by_id(ids[1])
        if phone1 and phone2 and callback.message:
            result = _compare_service.compare([phone1, phone2])
            await callback.message.answer(
                _compare_service.format_telegram(result),
                parse_mode="HTML",
            )
        await state.update_data(compare_ids=[])
        await callback.answer("Comparison ready!")
    else:
        await callback.answer(f"Phone added ({len(ids)}/2)")
