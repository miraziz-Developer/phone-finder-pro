from dataclasses import dataclass

from app.domain.entities.phone import Phone
from app.domain.entities.recommendation import ScoredPhone


@dataclass(slots=True)
class RecommendationRequestDTO:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str
    budget_min: float
    budget_max: float
    use_case: str
    preferred_brand: str
    min_ram_gb: int
    min_storage_gb: int
    requires_5g: bool
    requires_nfc: bool
    requires_wireless_charging: bool
    requires_esim: bool
    requires_amoled: bool
    requires_high_refresh: bool


@dataclass(slots=True)
class RecommendationResultDTO:
    recommendation_id: int
    phones: list[ScoredPhone]
    phone_details: list[Phone]
