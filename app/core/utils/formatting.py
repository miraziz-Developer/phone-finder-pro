from decimal import Decimal

from app.shared.constants import MESSAGE_SEPARATOR


def format_currency(amount: Decimal | float) -> str:
    return f"${float(amount):,.0f}"


def format_score_bar(score: float, width: int = 10) -> str:
    filled = int(score * width)
    return "█" * filled + "░" * (width - filled)


def format_phone_card(
    *,
    name: str,
    brand: str,
    price: Decimal,
    cpu: str,
    ram_gb: int,
    storage_gb: int,
    battery_mah: int,
    camera_mp: str,
    advantages: list[str],
    disadvantages: list[str],
    reason: str,
    score: float,
    rank: int,
) -> str:
    adv = "\n".join(f"  ✅ {a}" for a in advantages[:3])
    dis = "\n".join(f"  ⚠️ {d}" for d in disadvantages[:3])
    bar = format_score_bar(score)

    return (
        f"🏆 <b>#{rank} {name}</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        f"📱 {brand} · 💰 <b>{format_currency(price)}</b>\n"
        f"⚙️ {cpu}\n"
        f"🧠 {ram_gb} GB · 💾 {storage_gb} GB · 🔋 {battery_mah} mAh\n"
        f"📷 {camera_mp}\n"
        f"{MESSAGE_SEPARATOR}\n"
        f"📊 {bar} <b>{score:.0%}</b>\n"
        f"{MESSAGE_SEPARATOR}\n"
        f"<b>Pros</b>\n{adv}\n"
        f"<b>Cons</b>\n{dis}\n"
        f"{MESSAGE_SEPARATOR}\n"
        f"💡 <i>{reason}</i>"
    )
