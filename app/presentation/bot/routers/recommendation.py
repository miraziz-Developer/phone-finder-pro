"""Recommendation FSM flow router."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender

from app.application.commands import CreateRecommendationCommand, RegisterUserCommand
from app.application.dto import RecommendationRequestDTO
from app.application.handlers import CreateRecommendationHandler, RegisterUserHandler
from app.application.validators import (
    validate_brand,
    validate_budget,
    validate_ram,
    validate_storage,
    validate_use_case,
    validate_yes_no,
)
from app.core.database.unit_of_work import UnitOfWork
from app.core.utils.formatting import format_phone_card
from app.presentation.bot.keyboards import (
    brand_keyboard,
    confirm_keyboard,
    main_menu_keyboard,
    navigation_keyboard,
    ram_keyboard,
    results_navigation_inline,
    storage_keyboard,
    use_case_keyboard,
    yes_no_keyboard,
)
from app.presentation.bot.states import RecommendationStates
from app.presentation.bot.texts import (
    AMOLED_PROMPT,
    BRAND_PROMPT,
    BUDGET_PROMPT,
    CONFIRM_PROMPT,
    ESIM_PROMPT,
    FIVE_G_PROMPT,
    HIGH_REFRESH_PROMPT,
    LOADING_RECOMMENDATIONS,
    NFC_PROMPT,
    NO_RESULTS,
    RAM_PROMPT,
    STORAGE_PROMPT,
    USE_CASE_PROMPT,
    WIRELESS_CHARGING_PROMPT,
    format_preferences_summary,
)
from app.shared.exceptions import RecommendationError, ValidationError

router = Router(name="recommendation")

# Step order for back navigation
_STEP_ORDER = [
    RecommendationStates.budget,
    RecommendationStates.use_case,
    RecommendationStates.brand,
    RecommendationStates.ram,
    RecommendationStates.storage,
    RecommendationStates.five_g,
    RecommendationStates.nfc,
    RecommendationStates.wireless_charging,
    RecommendationStates.esim,
    RecommendationStates.amoled,
    RecommendationStates.high_refresh,
    RecommendationStates.confirm,
]

_STEP_PROMPTS = {
    RecommendationStates.budget: (BUDGET_PROMPT, navigation_keyboard(show_back=False)),
    RecommendationStates.use_case: (USE_CASE_PROMPT, use_case_keyboard()),
    RecommendationStates.brand: (BRAND_PROMPT, brand_keyboard()),
    RecommendationStates.ram: (RAM_PROMPT, ram_keyboard()),
    RecommendationStates.storage: (STORAGE_PROMPT, storage_keyboard()),
    RecommendationStates.five_g: (FIVE_G_PROMPT, yes_no_keyboard()),
    RecommendationStates.nfc: (NFC_PROMPT, yes_no_keyboard()),
    RecommendationStates.wireless_charging: (WIRELESS_CHARGING_PROMPT, yes_no_keyboard()),
    RecommendationStates.esim: (ESIM_PROMPT, yes_no_keyboard()),
    RecommendationStates.amoled: (AMOLED_PROMPT, yes_no_keyboard()),
    RecommendationStates.high_refresh: (HIGH_REFRESH_PROMPT, yes_no_keyboard()),
}


async def _go_back(message: Message, state: FSMContext) -> bool:
    """Navigate to previous FSM step. Returns True if back was handled."""
    current = await state.get_state()
    if current is None:
        return False

    state_map = {s.state: i for i, s in enumerate(_STEP_ORDER)}
    idx = state_map.get(current)
    if idx is None or idx == 0:
        return False

    prev_state = _STEP_ORDER[idx - 1]
    await state.set_state(prev_state)
    prompt, keyboard = _STEP_PROMPTS[prev_state]
    await message.answer(prompt, reply_markup=keyboard, parse_mode="HTML")
    return True


@router.message(Command("recommend"))
@router.message(F.text == "🔍 Find My Phone")
async def start_recommendation(message: Message, state: FSMContext) -> None:
    """Begin the recommendation questionnaire."""
    await state.clear()
    await state.set_state(RecommendationStates.budget)
    await message.answer(
        BUDGET_PROMPT, reply_markup=navigation_keyboard(show_back=False), parse_mode="HTML"
    )


@router.message(RecommendationStates.budget, F.text == "⬅️ Back")
@router.message(RecommendationStates.use_case, F.text == "⬅️ Back")
@router.message(RecommendationStates.brand, F.text == "⬅️ Back")
@router.message(RecommendationStates.ram, F.text == "⬅️ Back")
@router.message(RecommendationStates.storage, F.text == "⬅️ Back")
@router.message(RecommendationStates.five_g, F.text == "⬅️ Back")
@router.message(RecommendationStates.nfc, F.text == "⬅️ Back")
@router.message(RecommendationStates.wireless_charging, F.text == "⬅️ Back")
@router.message(RecommendationStates.esim, F.text == "⬅️ Back")
@router.message(RecommendationStates.amoled, F.text == "⬅️ Back")
@router.message(RecommendationStates.high_refresh, F.text == "⬅️ Back")
async def handle_back(message: Message, state: FSMContext) -> None:
    """Handle back button in recommendation flow."""
    if not await _go_back(message, state):
        await state.clear()
        await message.answer("Already at the first step.", reply_markup=main_menu_keyboard())


@router.message(RecommendationStates.budget)
async def process_budget(message: Message, state: FSMContext) -> None:
    """Process budget input."""
    if message.text is None:
        return
    try:
        budget_min, budget_max = validate_budget(message.text)
        await state.update_data(budget_min=float(budget_min), budget_max=float(budget_max))
        await state.set_state(RecommendationStates.use_case)
        await message.answer(USE_CASE_PROMPT, reply_markup=use_case_keyboard(), parse_mode="HTML")
    except ValidationError as exc:
        await message.answer(f"⚠️ {exc.message}\n\n{BUDGET_PROMPT}", parse_mode="HTML")


@router.message(RecommendationStates.use_case)
async def process_use_case(message: Message, state: FSMContext) -> None:
    """Process use case selection."""
    if message.text is None:
        return
    try:
        use_case = validate_use_case(
            message.text.replace("🎮 ", "")
            .replace("📷 ", "")
            .replace("💼 ", "")
            .replace("📱 ", "")
            .replace("🎬 ", "")
        )
        await state.update_data(use_case=use_case.value)
        await state.set_state(RecommendationStates.brand)
        await message.answer(BRAND_PROMPT, reply_markup=brand_keyboard(), parse_mode="HTML")
    except ValidationError as exc:
        await message.answer(f"⚠️ {exc.message}", parse_mode="HTML")


@router.message(RecommendationStates.brand)
async def process_brand(message: Message, state: FSMContext) -> None:
    """Process brand selection."""
    if message.text is None:
        return
    try:
        brand = validate_brand(
            message.text.replace("🍎 ", "")
            .replace("📱 ", "")
            .replace("📲 ", "")
            .replace("🔍 ", "")
            .replace("✨ ", "")
            .replace("🔄 ", "")
        )
        await state.update_data(brand=brand.value)
        await state.set_state(RecommendationStates.ram)
        await message.answer(RAM_PROMPT, reply_markup=ram_keyboard(), parse_mode="HTML")
    except ValidationError as exc:
        await message.answer(f"⚠️ {exc.message}", parse_mode="HTML")


@router.message(RecommendationStates.ram)
async def process_ram(message: Message, state: FSMContext) -> None:
    """Process RAM selection."""
    if message.text is None:
        return
    try:
        ram = validate_ram(message.text)
        await state.update_data(ram=ram)
        await state.set_state(RecommendationStates.storage)
        await message.answer(STORAGE_PROMPT, reply_markup=storage_keyboard(), parse_mode="HTML")
    except ValidationError as exc:
        await message.answer(f"⚠️ {exc.message}", parse_mode="HTML")


@router.message(RecommendationStates.storage)
async def process_storage(message: Message, state: FSMContext) -> None:
    """Process storage selection."""
    if message.text is None:
        return
    try:
        storage = validate_storage(message.text)
        await state.update_data(storage=storage)
        await state.set_state(RecommendationStates.five_g)
        await message.answer(FIVE_G_PROMPT, reply_markup=yes_no_keyboard(), parse_mode="HTML")
    except ValidationError as exc:
        await message.answer(f"⚠️ {exc.message}", parse_mode="HTML")


async def _process_boolean_step(
    message: Message,
    state: FSMContext,
    field: str,
    next_state: RecommendationStates,
    next_prompt: str,
    next_keyboard,
) -> None:
    """Generic handler for yes/no FSM steps."""
    if message.text is None:
        return
    try:
        value = validate_yes_no(message.text)
        await state.update_data(**{field: value})
        await state.set_state(next_state)
        await message.answer(next_prompt, reply_markup=next_keyboard, parse_mode="HTML")
    except ValidationError as exc:
        await message.answer(f"⚠️ {exc.message}", parse_mode="HTML")


@router.message(RecommendationStates.five_g)
async def process_five_g(message: Message, state: FSMContext) -> None:
    await _process_boolean_step(
        message, state, "five_g", RecommendationStates.nfc, NFC_PROMPT, yes_no_keyboard()
    )


@router.message(RecommendationStates.nfc)
async def process_nfc(message: Message, state: FSMContext) -> None:
    await _process_boolean_step(
        message,
        state,
        "nfc",
        RecommendationStates.wireless_charging,
        WIRELESS_CHARGING_PROMPT,
        yes_no_keyboard(),
    )


@router.message(RecommendationStates.wireless_charging)
async def process_wireless(message: Message, state: FSMContext) -> None:
    await _process_boolean_step(
        message,
        state,
        "wireless_charging",
        RecommendationStates.esim,
        ESIM_PROMPT,
        yes_no_keyboard(),
    )


@router.message(RecommendationStates.esim)
async def process_esim(message: Message, state: FSMContext) -> None:
    await _process_boolean_step(
        message, state, "esim", RecommendationStates.amoled, AMOLED_PROMPT, yes_no_keyboard()
    )


@router.message(RecommendationStates.amoled)
async def process_amoled(message: Message, state: FSMContext) -> None:
    await _process_boolean_step(
        message,
        state,
        "amoled",
        RecommendationStates.high_refresh,
        HIGH_REFRESH_PROMPT,
        yes_no_keyboard(),
    )


@router.message(RecommendationStates.high_refresh)
async def process_high_refresh(message: Message, state: FSMContext) -> None:
    """Process high refresh rate and show confirmation."""
    if message.text is None:
        return
    try:
        value = validate_yes_no(message.text)
        await state.update_data(high_refresh=value)
        data = await state.get_data()
        summary = format_preferences_summary(data)
        await state.set_state(RecommendationStates.confirm)
        await message.answer(
            CONFIRM_PROMPT.format(summary=summary),
            reply_markup=confirm_keyboard(),
            parse_mode="HTML",
        )
    except ValidationError as exc:
        await message.answer(f"⚠️ {exc.message}", parse_mode="HTML")


@router.message(RecommendationStates.confirm, F.text == "✏️ Edit")
async def edit_preferences(message: Message, state: FSMContext) -> None:
    """Restart from budget step."""
    await state.set_state(RecommendationStates.budget)
    await message.answer(
        BUDGET_PROMPT, reply_markup=navigation_keyboard(show_back=False), parse_mode="HTML"
    )


@router.message(RecommendationStates.confirm, F.text == "✅ Confirm & Search")
async def confirm_and_search(message: Message, state: FSMContext, uow: UnitOfWork) -> None:
    """Execute recommendation engine and display results."""
    if message.from_user is None:
        return

    data = await state.get_data()
    await state.set_state(RecommendationStates.results)

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await message.answer(LOADING_RECOMMENDATIONS, parse_mode="HTML")

        reg_handler = RegisterUserHandler(uow)
        await reg_handler.handle(
            RegisterUserCommand(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code or "en",
            )
        )

        try:
            handler = CreateRecommendationHandler(uow)
            result = await handler.handle(
                CreateRecommendationCommand(
                    request=RecommendationRequestDTO(
                        telegram_id=message.from_user.id,
                        username=message.from_user.username,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name,
                        language_code=message.from_user.language_code or "en",
                        budget_min=data["budget_min"],
                        budget_max=data["budget_max"],
                        use_case=data["use_case"],
                        preferred_brand=data["brand"],
                        min_ram_gb=data["ram"],
                        min_storage_gb=data["storage"],
                        requires_5g=data["five_g"],
                        requires_nfc=data["nfc"],
                        requires_wireless_charging=data["wireless_charging"],
                        requires_esim=data["esim"],
                        requires_amoled=data["amoled"],
                        requires_high_refresh=data["high_refresh"],
                    )
                )
            )
        except RecommendationError:
            await message.answer(NO_RESULTS, reply_markup=main_menu_keyboard(), parse_mode="HTML")
            await state.clear()
            return

        await state.update_data(
            result_phones=[s.phone_id for s in result.phones],
            result_index=0,
        )

        await _send_result_card(message, result, 0)


async def _send_result_card(message: Message, result, index: int) -> None:
    """Send a single recommendation result card."""
    scored = result.phones[index]
    phone = next((p for p in result.phone_details if p.id == scored.phone_id), None)
    if phone is None:
        return

    card = format_phone_card(
        name=phone.name,
        brand=phone.brand_name or scored.brand_name,
        price=phone.price,
        cpu=phone.cpu,
        ram_gb=phone.ram_gb,
        storage_gb=phone.storage_gb,
        battery_mah=phone.battery_mah,
        camera_mp=phone.camera_description,
        advantages=phone.advantages,
        disadvantages=phone.disadvantages,
        reason=scored.reason,
        score=scored.score,
        rank=index + 1,
    )

    if phone.primary_image_url:
        await message.answer_photo(
            photo=phone.primary_image_url,
            caption=card,
            parse_mode="HTML",
            reply_markup=results_navigation_inline(index, len(result.phones)),
        )
    else:
        await message.answer(
            card,
            parse_mode="HTML",
            reply_markup=results_navigation_inline(index, len(result.phones)),
        )


@router.callback_query(F.data.startswith("result:"))
async def handle_result_navigation(
    callback: CallbackQuery,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle result pagination callbacks."""
    if callback.data is None or callback.message is None:
        return

    parts = callback.data.split(":")
    action = parts[1]

    if action == "new":
        await state.clear()
        await state.set_state(RecommendationStates.budget)
        await callback.message.answer(
            BUDGET_PROMPT,
            reply_markup=navigation_keyboard(show_back=False),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    if action == "menu":
        await state.clear()
        from app.presentation.bot.texts import WELCOME

        await callback.message.answer(WELCOME, reply_markup=main_menu_keyboard(), parse_mode="HTML")
        await callback.answer()
        return

    data = await state.get_data()
    phone_ids: list[int] = data.get("result_phones", [])
    current_index: int = data.get("result_index", 0)

    if action == "prev":
        current_index = max(0, current_index - 1)
    elif action == "next":
        current_index = min(len(phone_ids) - 1, current_index + 1)

    await state.update_data(result_index=current_index)
    await callback.answer()
