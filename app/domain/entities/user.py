"""User domain entity."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    """Telegram user registered in the system."""

    id: int | None
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class UserPreference:
    """Captured user preferences from the recommendation flow."""

    id: int | None
    user_id: int
    budget_min: float
    budget_max: float
    use_case: str
    preferred_brand: str | None
    min_ram_gb: int
    min_storage_gb: int
    requires_5g: bool
    requires_nfc: bool
    requires_wireless_charging: bool
    requires_esim: bool
    requires_amoled: bool
    requires_high_refresh: bool
    created_at: datetime | None = None
