"""Bot message texts and templates."""

from app.shared.constants import MESSAGE_SEPARATOR

WELCOME = (
    "📱 <b>Phone Finder Pro</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "Your personal smartphone recommendation assistant.\n\n"
    "I'll help you find the perfect phone based on your "
    "budget, needs, and preferences.\n\n"
    "Choose an option below to get started:"
)

HELP = (
    "ℹ️ <b>How it works</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "1️⃣ Answer a few questions about your preferences\n"
    "2️⃣ Our engine scores every phone in our catalog\n"
    "3️⃣ Get top 5 personalized recommendations\n\n"
    "<b>Commands:</b>\n"
    "/start — Main menu\n"
    "/recommend — Start recommendation\n"
    "/search — Search phones\n"
    "/filter — Advanced filters\n"
    "/compare — Compare 2 phones\n"
    "/favorites — Your saved phones\n"
    "/popular — Most recommended phones\n"
    "/newest — Latest additions\n"
    "/history — Past recommendations\n"
    "/cancel — Cancel current flow"
)

# Recommendation flow prompts
BUDGET_PROMPT = (
    "💰 <b>Step 1/11 — Budget</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "What is your budget?\n\n"
    "Enter a single amount (e.g. <code>800</code>) or a range "
    "(e.g. <code>600-900</code>)."
)

USE_CASE_PROMPT = (
    "🎯 <b>Step 2/11 — Primary Use</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "What will you mainly use the phone for?"
)

BRAND_PROMPT = (
    "🏷️ <b>Step 3/11 — Brand Preference</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "Do you have a preferred brand?"
)

RAM_PROMPT = (
    "🧠 <b>Step 4/11 — Minimum RAM</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "What is the minimum RAM you need?"
)

STORAGE_PROMPT = (
    "💾 <b>Step 5/11 — Minimum Storage</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "What is the minimum storage you need?"
)

FIVE_G_PROMPT = (
    "📶 <b>Step 6/11 — 5G Support</b>\n" f"{MESSAGE_SEPARATOR}\n" "Do you need 5G connectivity?"
)

NFC_PROMPT = (
    "📡 <b>Step 7/11 — NFC</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "Do you need NFC for contactless payments?"
)

WIRELESS_CHARGING_PROMPT = (
    "🔋 <b>Step 8/11 — Wireless Charging</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "Do you need wireless charging?"
)

ESIM_PROMPT = "📲 <b>Step 9/11 — eSIM</b>\n" f"{MESSAGE_SEPARATOR}\n" "Do you need eSIM support?"

AMOLED_PROMPT = (
    "🖥️ <b>Step 10/11 — AMOLED Display</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "Do you need an AMOLED display?"
)

HIGH_REFRESH_PROMPT = (
    "⚡ <b>Step 11/11 — High Refresh Rate</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "Do you need a high refresh rate display (90Hz+)?"
)

CONFIRM_PROMPT = (
    "✅ <b>Review Your Preferences</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "{summary}\n"
    f"{MESSAGE_SEPARATOR}\n"
    "Ready to find your perfect phone?"
)

LOADING_RECOMMENDATIONS = (
    "🔍 <b>Analyzing catalog...</b>\n"
    "Scoring phones against your preferences.\n"
    "This may take a moment."
)

NO_RESULTS = (
    "😔 <b>No matches found</b>\n"
    f"{MESSAGE_SEPARATOR}\n"
    "We couldn't find phones matching all your criteria.\n"
    "Try relaxing some requirements or increasing your budget."
)

CANCELLED = (
    "❌ <b>Cancelled</b>\n"
    "Your current session has been cancelled.\n"
    "Use /start to return to the main menu."
)

RATE_LIMIT_MESSAGE = "⏳ <b>Too many requests</b>\n" "Please wait a moment before trying again."

ERROR_MESSAGE = (
    "⚠️ <b>Something went wrong</b>\n" "An unexpected error occurred. Please try again later."
)


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def format_preferences_summary(data: dict) -> str:
    return (
        f"💰 Budget: <b>${data.get('budget_min', 0):,.0f} – ${data.get('budget_max', 0):,.0f}</b>\n"
        f"🎯 Use case: <b>{data.get('use_case', '—')}</b>\n"
        f"🏷️ Brand: <b>{data.get('brand', '—')}</b>\n"
        f"🧠 RAM: <b>{data.get('ram', '—')} GB</b>\n"
        f"💾 Storage: <b>{data.get('storage', '—')} GB</b>\n"
        f"📶 5G: <b>{_yes_no(data.get('five_g', False))}</b>\n"
        f"📡 NFC: <b>{_yes_no(data.get('nfc', False))}</b>\n"
        f"🔋 Wireless: <b>{_yes_no(data.get('wireless_charging', False))}</b>\n"
        f"📲 eSIM: <b>{_yes_no(data.get('esim', False))}</b>\n"
        f"🖥️ AMOLED: <b>{_yes_no(data.get('amoled', False))}</b>\n"
        f"⚡ 120Hz+: <b>{_yes_no(data.get('high_refresh', False))}</b>"
    )
