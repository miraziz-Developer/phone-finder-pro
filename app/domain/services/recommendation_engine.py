from dataclasses import dataclass, field

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.domain.entities.phone import Phone
from app.domain.entities.recommendation import ScoredPhone
from app.domain.value_objects import UserPreferencesInput
from app.shared.enums import BrandName, UseCase

logger = get_logger(__name__)

_USE_CASE_BOOST: dict[UseCase, dict[str, float]] = {
    UseCase.GAMING: {"performance": 1.3, "display": 1.2, "battery": 1.1},
    UseCase.PHOTOGRAPHY: {"camera": 1.4, "storage": 1.1},
    UseCase.BUSINESS: {"battery": 1.2, "performance": 1.1},
    UseCase.DAILY_USE: {"battery": 1.15, "performance": 1.05},
    UseCase.CONTENT_CREATION: {"camera": 1.3, "storage": 1.2, "display": 1.15},
}

_FEATURE_FLAGS: tuple[tuple[str, str], ...] = (
    ("requires_5g", "has_5g"),
    ("requires_nfc", "has_nfc"),
    ("requires_wireless_charging", "has_wireless_charging"),
    ("requires_esim", "has_esim"),
    ("requires_amoled", "has_amoled"),
    ("requires_high_refresh", "has_high_refresh"),
)


@dataclass
class RecommendationEngine:
    settings: Settings = field(default_factory=get_settings)

    def score_phones(
        self,
        phones: list[Phone],
        preferences: UserPreferencesInput,
    ) -> list[ScoredPhone]:
        weights = self.settings.score_weights
        scored: list[ScoredPhone] = []

        for phone in phones:
            breakdown = {
                "budget": self._score_budget(phone, preferences) * weights["budget"],
                "performance": self._score_performance(phone, preferences) * weights["performance"],
                "camera": self._score_camera(phone, preferences) * weights["camera"],
                "battery": self._score_battery(phone) * weights["battery"],
                "display": self._score_display(phone) * weights["display"],
                "storage": self._score_storage(phone, preferences) * weights["storage"],
                "brand": self._score_brand(phone, preferences) * weights["brand"],
                "features": self._score_features(phone, preferences) * weights["features"],
            }
            total = round(sum(breakdown.values()), 4)

            if total < self.settings.recommendation_min_score:
                continue

            scored.append(
                ScoredPhone(
                    phone_id=phone.id or 0,
                    phone_name=phone.name,
                    brand_name=phone.brand_name or "Unknown",
                    price=phone.price,
                    score=total,
                    reason=self._build_reason(phone, preferences, breakdown),
                    score_breakdown=breakdown,
                )
            )

        scored.sort(key=lambda s: s.score, reverse=True)
        result = scored[: self.settings.recommendation_top_n]
        logger.info("recommendation_scored", candidates=len(phones), returned=len(result))
        return result

    def _score_budget(self, phone: Phone, prefs: UserPreferencesInput) -> float:
        price = float(phone.price)
        if prefs.budget.min_amount <= phone.price <= prefs.budget.max_amount:
            return 1.0
        tolerance = float(prefs.budget.midpoint) * self.settings.budget_tolerance_ratio
        if price < float(prefs.budget.min_amount):
            return max(0.0, 1.0 - (float(prefs.budget.min_amount) - price) / tolerance) * 0.8
        return max(0.0, 1.0 - (price - float(prefs.budget.max_amount)) / tolerance)

    def _score_performance(self, phone: Phone, prefs: UserPreferencesInput) -> float:
        boost = _USE_CASE_BOOST.get(prefs.use_case, {}).get("performance", 1.0)
        return min(1.0, phone.performance_score / 100.0 * boost)

    def _score_camera(self, phone: Phone, prefs: UserPreferencesInput) -> float:
        boost = _USE_CASE_BOOST.get(prefs.use_case, {}).get("camera", 1.0)
        return min(1.0, phone.camera_score / 100.0 * boost)

    def _score_battery(self, phone: Phone) -> float:
        return phone.battery_score / 100.0

    def _score_display(self, phone: Phone) -> float:
        return phone.display_score / 100.0

    def _score_storage(self, phone: Phone, prefs: UserPreferencesInput) -> float:
        if phone.storage_gb >= prefs.min_storage_gb:
            bonus = min((phone.storage_gb - prefs.min_storage_gb) / 256.0, 0.2)
            return min(1.0, 0.8 + bonus)
        return max(0.0, 1.0 - (prefs.min_storage_gb - phone.storage_gb) * 0.15)

    def _score_brand(self, phone: Phone, prefs: UserPreferencesInput) -> float:
        if prefs.preferred_brand == BrandName.NO_PREFERENCE:
            return 0.7
        if phone.brand_name and phone.brand_name.lower() == prefs.preferred_brand.value:
            return 1.0
        return 0.2

    def _score_features(self, phone: Phone, prefs: UserPreferencesInput) -> float:
        if phone.features is None:
            return 0.5
        required, matched = [], []
        for pref_attr, feat_attr in _FEATURE_FLAGS:
            if getattr(prefs, pref_attr):
                required.append(True)
                matched.append(getattr(phone.features, feat_attr, False))
        return sum(matched) / len(required) if required else 0.8

    def _build_reason(
        self,
        phone: Phone,
        prefs: UserPreferencesInput,
        breakdown: dict[str, float],
    ) -> str:
        top = max(breakdown, key=lambda k: breakdown[k])
        labels = {
            "budget": f"great value at ${phone.price:,.0f}",
            "performance": f"strong {phone.cpu}",
            "camera": f"{phone.camera_main_mp:.0f}MP camera",
            "battery": f"{phone.battery_mah}mAh battery",
            "display": "quality display",
            "storage": f"{phone.storage_gb}GB storage",
            "brand": f"matches {prefs.preferred_brand.value}",
            "features": "has required features",
        }
        parts = [labels.get(top, "solid match")]
        if phone.discount_percent and phone.discount_percent > 0:
            parts.append(f"{phone.discount_percent:.0f}% off")
        return "Picked for " + ", ".join(parts[:2]) + "."
