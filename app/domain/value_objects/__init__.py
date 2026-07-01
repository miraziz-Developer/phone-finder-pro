"""Domain value objects."""

from dataclasses import dataclass
from decimal import Decimal

from app.shared.enums import BrandName, UseCase


@dataclass(frozen=True, slots=True)
class BudgetRange:
    """Validated budget range in USD."""

    min_amount: Decimal
    max_amount: Decimal

    def __post_init__(self) -> None:
        if self.min_amount < 0:
            raise ValueError("Minimum budget cannot be negative")
        if self.max_amount < self.min_amount:
            raise ValueError("Maximum budget must be >= minimum budget")

    @property
    def midpoint(self) -> Decimal:
        """Return the midpoint of the budget range."""
        return (self.min_amount + self.max_amount) / 2


@dataclass(frozen=True, slots=True)
class UserPreferencesInput:
    """Immutable value object for recommendation input."""

    budget: BudgetRange
    use_case: UseCase
    preferred_brand: BrandName
    min_ram_gb: int
    min_storage_gb: int
    requires_5g: bool
    requires_nfc: bool
    requires_wireless_charging: bool
    requires_esim: bool
    requires_amoled: bool
    requires_high_refresh: bool

    def __post_init__(self) -> None:
        if self.min_ram_gb < 2:
            raise ValueError("Minimum RAM must be at least 2 GB")
        if self.min_storage_gb < 32:
            raise ValueError("Minimum storage must be at least 32 GB")
