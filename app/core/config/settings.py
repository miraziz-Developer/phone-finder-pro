from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    app_name: str = "phone-marketplace-bot"
    default_currency: str = "USD"

    bot_token: str = Field(..., min_length=10)
    admin_ids: list[int] = Field(default_factory=list)

    api_enabled: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    jwt_secret_key: str = Field(default="change-me-in-production-use-long-random-string")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    api_admin_username: str = "admin"
    api_admin_password: str = Field(default="admin_secret_change_me")

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "phonebot"
    postgres_password: str = "phonebot_secret"
    postgres_db: str = "phonebot"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    cache_ttl_seconds: int = 300
    cache_enabled: bool = True

    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60

    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"

    pagination_page_size: int = 5
    pagination_max_page_size: int = 50

    recommendation_top_n: int = 5
    recommendation_min_score: float = 0.3
    score_weight_budget: float = 0.30
    score_weight_performance: float = 0.20
    score_weight_camera: float = 0.15
    score_weight_battery: float = 0.10
    score_weight_display: float = 0.10
    score_weight_storage: float = 0.05
    score_weight_brand: float = 0.05
    score_weight_features: float = 0.05
    budget_tolerance_ratio: float = 0.15

    comparison_max_phones: int = 2
    import_max_rows: int = 500
    import_batch_size: int = 50
    min_budget_usd: float = 100.0
    max_budget_usd: float = 5000.0

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: str | list[int]) -> list[int]:
        if isinstance(value, list):
            return value
        if not value or not str(value).strip():
            return []
        return [int(item.strip()) for item in str(value).split(",") if item.strip()]

    @property
    def score_weights(self) -> dict[str, float]:
        return {
            "budget": self.score_weight_budget,
            "performance": self.score_weight_performance,
            "camera": self.score_weight_camera,
            "battery": self.score_weight_battery,
            "display": self.score_weight_display,
            "storage": self.score_weight_storage,
            "brand": self.score_weight_brand,
            "features": self.score_weight_features,
        }

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def postgres_dsn_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return (
                f"redis://:{self.redis_password}@{self.redis_host}:"
                f"{self.redis_port}/{self.redis_db}"
            )
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
