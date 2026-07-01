"""Recommendation domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class ScoredPhone:
    """Phone with computed recommendation score and explanation."""

    phone_id: int
    phone_name: str
    brand_name: str
    price: Decimal
    score: float
    reason: str
    score_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class Recommendation:
    """A recommendation session linking user preferences to results."""

    id: int | None
    user_id: int
    preference_id: int
    created_at: datetime | None = None
    results: list[ScoredPhone] = field(default_factory=list)


@dataclass(slots=True)
class RecommendationHistory:
    """Historical record of a single recommended phone."""

    id: int | None
    recommendation_id: int
    phone_id: int
    score: float
    rank: int
    reason: str
    created_at: datetime | None = None
