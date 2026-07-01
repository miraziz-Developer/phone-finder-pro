"""Telegram keyboard builders."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from app.shared.constants import RAM_OPTIONS, STORAGE_OPTIONS


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu reply keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Find My Phone"), KeyboardButton(text="📱 Browse Phones")],
            [KeyboardButton(text="⭐ Favorites"), KeyboardButton(text="📊 Popular")],
            [KeyboardButton(text="🆕 Newest"), KeyboardButton(text="📜 History")],
            [KeyboardButton(text="ℹ️ Help")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose an action...",
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    """Remove reply keyboard."""
    return ReplyKeyboardRemove()


def navigation_keyboard(*, show_back: bool = True, show_cancel: bool = True) -> ReplyKeyboardMarkup:
    """Back and cancel navigation buttons."""
    row = []
    if show_back:
        row.append(KeyboardButton(text="⬅️ Back"))
    if show_cancel:
        row.append(KeyboardButton(text="❌ Cancel"))
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def use_case_keyboard() -> ReplyKeyboardMarkup:
    """Use case selection keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Gaming"), KeyboardButton(text="📷 Photography")],
            [KeyboardButton(text="💼 Business"), KeyboardButton(text="📱 Daily Use")],
            [KeyboardButton(text="🎬 Content Creation")],
            [KeyboardButton(text="⬅️ Back"), KeyboardButton(text="❌ Cancel")],
        ],
        resize_keyboard=True,
    )


def brand_keyboard() -> ReplyKeyboardMarkup:
    """Brand selection keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍎 Apple"), KeyboardButton(text="📱 Samsung")],
            [KeyboardButton(text="📲 Xiaomi"), KeyboardButton(text="🔍 Google")],
            [KeyboardButton(text="✨ Nothing"), KeyboardButton(text="🔄 No Preference")],
            [KeyboardButton(text="⬅️ Back"), KeyboardButton(text="❌ Cancel")],
        ],
        resize_keyboard=True,
    )


def ram_keyboard() -> ReplyKeyboardMarkup:
    """RAM selection keyboard."""
    rows = []
    for i in range(0, len(RAM_OPTIONS), 3):
        chunk = RAM_OPTIONS[i : i + 3]
        rows.append([KeyboardButton(text=f"{r} GB") for r in chunk])
    rows.append([KeyboardButton(text="⬅️ Back"), KeyboardButton(text="❌ Cancel")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def storage_keyboard() -> ReplyKeyboardMarkup:
    """Storage selection keyboard."""
    rows = []
    for i in range(0, len(STORAGE_OPTIONS), 3):
        chunk = STORAGE_OPTIONS[i : i + 3]
        rows.append([KeyboardButton(text=f"{s} GB") for s in chunk])
    rows.append([KeyboardButton(text="⬅️ Back"), KeyboardButton(text="❌ Cancel")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def yes_no_keyboard() -> ReplyKeyboardMarkup:
    """Yes/No selection keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Yes"), KeyboardButton(text="❌ No")],
            [KeyboardButton(text="⬅️ Back"), KeyboardButton(text="❌ Cancel")],
        ],
        resize_keyboard=True,
    )


def confirm_keyboard() -> ReplyKeyboardMarkup:
    """Confirmation keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Confirm & Search"), KeyboardButton(text="✏️ Edit")],
            [KeyboardButton(text="❌ Cancel")],
        ],
        resize_keyboard=True,
    )


def phone_list_inline(phones) -> InlineKeyboardMarkup:
    """Open phone detail cards from a search/browse list."""
    rows = []
    for phone in phones:
        if phone.id is not None:
            rows.append(
                [
                    InlineKeyboardButton(
                        text=f"📱 {phone.name}",
                        callback_data=f"phone:{phone.id}",
                    )
                ]
            )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def compare_picker_inline(phones, *, exclude_id: int | None = None) -> InlineKeyboardMarkup:
    """Pick phones for side-by-side comparison."""
    rows = []
    for phone in phones:
        if phone.id is None or phone.id == exclude_id:
            continue
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"⚖️ {phone.name}",
                    callback_data=f"cmp:{phone.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cmp:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def phone_actions_inline(phone_id: int, is_favorite: bool = False) -> InlineKeyboardMarkup:
    """Inline actions for a phone card."""
    fav_text = "💔 Remove Favorite" if is_favorite else "⭐ Add to Favorites"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=fav_text, callback_data=f"fav:{phone_id}"),
                InlineKeyboardButton(text="📊 Compare", callback_data=f"cmp:{phone_id}"),
            ],
            [InlineKeyboardButton(text="🔍 View Details", callback_data=f"phone:{phone_id}")],
        ]
    )


def pagination_inline(
    prefix: str,
    page: int,
    total_pages: int,
    extra_id: str = "",
) -> InlineKeyboardMarkup:
    """Build pagination inline keyboard."""
    buttons = []
    if page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="◀️ Prev", callback_data=f"{prefix}:page:{page - 1}:{extra_id}"
            )
        )
    buttons.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        buttons.append(
            InlineKeyboardButton(
                text="Next ▶️", callback_data=f"{prefix}:page:{page + 1}:{extra_id}"
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def results_navigation_inline(current: int, total: int) -> InlineKeyboardMarkup:
    """Navigation for recommendation results."""
    buttons = []
    if current > 0:
        buttons.append(
            InlineKeyboardButton(text="◀️ Previous", callback_data=f"result:prev:{current}")
        )
    if current < total - 1:
        buttons.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"result:next:{current}"))
    row2 = [
        InlineKeyboardButton(text="🔄 New Search", callback_data="result:new"),
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="result:menu"),
    ]
    rows = [buttons] if buttons else []
    rows.append(row2)
    return InlineKeyboardMarkup(inline_keyboard=rows)
