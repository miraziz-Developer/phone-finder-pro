from dataclasses import dataclass

from app.shared.enums import PhoneSortOrder


@dataclass(frozen=True, slots=True)
class GetPhoneByIdQuery:
    phone_id: int


@dataclass(frozen=True, slots=True)
class SearchPhonesQuery:
    brand_id: int | None = None
    min_price: float | None = None
    max_price: float | None = None
    query: str | None = None
    sort: PhoneSortOrder = PhoneSortOrder.SCORE
    offset: int = 0
    limit: int = 10


@dataclass(frozen=True, slots=True)
class GetUserFavoritesQuery:
    user_id: int


@dataclass(frozen=True, slots=True)
class GetRecommendationHistoryQuery:
    user_id: int
    limit: int = 5
