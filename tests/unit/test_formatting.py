from decimal import Decimal

from app.core.utils.formatting import format_currency, format_phone_card, format_score_bar


def test_format_currency() -> None:
    assert format_currency(Decimal("999")) == "$999"


def test_format_score_bar() -> None:
    bar = format_score_bar(0.5, width=10)
    assert len(bar) == 10
    assert "█" in bar


def test_format_phone_card() -> None:
    card = format_phone_card(
        name="Test Phone",
        brand="Samsung",
        price=Decimal("799"),
        cpu="Snapdragon 8",
        ram_gb=12,
        storage_gb=256,
        battery_mah=5000,
        camera_mp="50MP",
        advantages=["Fast"],
        disadvantages=["Pricey"],
        reason="Strong match.",
        score=0.87,
        rank=1,
    )
    assert "Test Phone" in card
    assert "87%" in card
