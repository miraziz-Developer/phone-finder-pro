from decimal import Decimal

import pytest

from app.application.services.compare import PhoneCompareService
from app.domain.entities.phone import Phone


def _phone(name: str, price: int, **scores: float) -> Phone:
    return Phone(
        id=1,
        brand_id=1,
        category_id=1,
        name=name,
        slug=name.lower().replace(" ", "-"),
        model_year=2025,
        price=Decimal(str(price)),
        currency="USD",
        cpu="CPU",
        gpu=None,
        ram_gb=8,
        storage_gb=128,
        battery_mah=5000,
        camera_main_mp=50,
        camera_ultra_mp=None,
        camera_tele_mp=None,
        camera_front_mp=12,
        performance_score=scores.get("perf", 80),
        camera_score=scores.get("camera", 80),
        battery_score=scores.get("battery", 80),
        display_score=scores.get("display", 80),
        brand_name="Test",
    )


def test_compare_two_phones() -> None:
    service = PhoneCompareService()
    result = service.compare(
        [
            _phone("Phone A", 799, perf=92, camera=90),
            _phone("Phone B", 499, perf=70, camera=75),
        ]
    )
    assert result.overall_winner_index in (0, 1)
    assert "Phone A" in service.format_telegram(result)


def test_compare_requires_two() -> None:
    with pytest.raises(ValueError):
        PhoneCompareService().compare([_phone("Solo", 599)])
