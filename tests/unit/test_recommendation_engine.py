from decimal import Decimal

from app.domain.entities.phone import Phone, PhoneFeatures
from app.domain.services.recommendation_engine import RecommendationEngine
from app.domain.value_objects import BudgetRange, UserPreferencesInput
from app.shared.enums import BrandName, UseCase


def _budget_phone() -> Phone:
    phone = Phone(
        id=2,
        brand_id=2,
        category_id=1,
        name="Budget Phone",
        slug="budget-phone",
        model_year=2024,
        price=Decimal("199"),
        currency="USD",
        cpu="Snapdragon 4",
        gpu=None,
        ram_gb=4,
        storage_gb=64,
        battery_mah=4000,
        camera_main_mp=48.0,
        camera_ultra_mp=None,
        camera_tele_mp=None,
        camera_front_mp=8.0,
        performance_score=40.0,
        camera_score=50.0,
        battery_score=70.0,
        display_score=60.0,
        brand_name="Xiaomi",
    )
    phone.features = PhoneFeatures(
        id=2,
        phone_id=2,
        has_5g=False,
        has_nfc=False,
        has_wireless_charging=False,
        has_esim=False,
        has_amoled=False,
        has_high_refresh=False,
        refresh_rate_hz=60,
        display_size_inches=6.5,
        display_resolution="1600x720",
        ip_rating=None,
        os_version="Android 13",
    )
    return phone


def test_score_phones_returns_top_matches(sample_phone, sample_preferences) -> None:
    engine = RecommendationEngine()
    results = engine.score_phones([sample_phone, _budget_phone()], sample_preferences)
    assert results
    assert results[0].phone_id == sample_phone.id
    assert results[0].score > 0.5


def test_budget_scoring_within_range(sample_phone) -> None:
    engine = RecommendationEngine()
    prefs = UserPreferencesInput(
        budget=BudgetRange(min_amount=Decimal("700"), max_amount=Decimal("900")),
        use_case=UseCase.DAILY_USE,
        preferred_brand=BrandName.NO_PREFERENCE,
        min_ram_gb=8,
        min_storage_gb=128,
        requires_5g=False,
        requires_nfc=False,
        requires_wireless_charging=False,
        requires_esim=False,
        requires_amoled=False,
        requires_high_refresh=False,
    )
    assert engine._score_budget(sample_phone, prefs) == 1.0


def test_brand_preference_match(sample_phone) -> None:
    engine = RecommendationEngine()
    prefs = UserPreferencesInput(
        budget=BudgetRange(min_amount=Decimal("500"), max_amount=Decimal("1000")),
        use_case=UseCase.DAILY_USE,
        preferred_brand=BrandName.SAMSUNG,
        min_ram_gb=8,
        min_storage_gb=128,
        requires_5g=False,
        requires_nfc=False,
        requires_wireless_charging=False,
        requires_esim=False,
        requires_amoled=False,
        requires_high_refresh=False,
    )
    assert engine._score_brand(sample_phone, prefs) == 1.0


def test_empty_catalog_returns_empty(sample_preferences) -> None:
    assert RecommendationEngine().score_phones([], sample_preferences) == []
