from dataclasses import dataclass

from app.application.dto import RecommendationRequestDTO


@dataclass(frozen=True, slots=True)
class CreateRecommendationCommand:
    request: RecommendationRequestDTO


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str = "en"


@dataclass(frozen=True, slots=True)
class ToggleFavoriteCommand:
    user_id: int
    phone_id: int
