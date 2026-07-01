"""Input validators for application commands."""

from decimal import Decimal, InvalidOperation

from app.core.config import get_settings
from app.shared.constants import RAM_OPTIONS, STORAGE_OPTIONS
from app.shared.enums import BrandName, UseCase
from app.shared.exceptions import ValidationError


def validate_budget(value: str) -> tuple[Decimal, Decimal]:
    """
    Parse and validate budget input.

    Accepts formats: "500", "400-600", "400 - 600"

    Returns:
        Tuple of (min_budget, max_budget).

    Raises:
        ValidationError: If the input is invalid.
    """
    cleaned = value.strip().replace("$", "").replace(",", "")

    if "-" in cleaned:
        parts = [p.strip() for p in cleaned.split("-", 1)]
        if len(parts) != 2:
            raise ValidationError("Invalid budget range format", field="budget")
        try:
            budget_min = Decimal(parts[0])
            budget_max = Decimal(parts[1])
        except InvalidOperation as exc:
            raise ValidationError("Budget must be a valid number", field="budget") from exc
    else:
        try:
            amount = Decimal(cleaned)
        except InvalidOperation as exc:
            raise ValidationError("Budget must be a valid number", field="budget") from exc
        budget_min = amount * Decimal("0.85")
        budget_max = amount

    cfg = get_settings()
    min_b, max_b = Decimal(str(cfg.min_budget_usd)), Decimal(str(cfg.max_budget_usd))
    if budget_min < min_b or budget_max > max_b:
        raise ValidationError(
            f"Budget must be between ${min_b:,.0f} and ${max_b:,.0f}",
            field="budget",
        )
    if budget_max < budget_min:
        raise ValidationError("Maximum budget must be >= minimum", field="budget")

    return budget_min, budget_max


def validate_ram(value: str) -> int:
    """Validate RAM selection."""
    try:
        ram = int(value.replace("GB", "").strip())
    except ValueError as exc:
        raise ValidationError("RAM must be a number in GB", field="ram") from exc

    if ram not in RAM_OPTIONS:
        raise ValidationError(
            f"RAM must be one of: {', '.join(map(str, RAM_OPTIONS))} GB",
            field="ram",
        )
    return ram


def validate_storage(value: str) -> int:
    """Validate storage selection."""
    try:
        storage = int(value.replace("GB", "").strip())
    except ValueError as exc:
        raise ValidationError("Storage must be a number in GB", field="storage") from exc

    if storage not in STORAGE_OPTIONS:
        opts = ", ".join(map(str, STORAGE_OPTIONS))
        raise ValidationError(f"Storage must be one of: {opts} GB", field="storage")
    return storage


def validate_use_case(value: str) -> UseCase:
    """Validate use case selection."""
    mapping = {
        "gaming": UseCase.GAMING,
        "photography": UseCase.PHOTOGRAPHY,
        "business": UseCase.BUSINESS,
        "daily use": UseCase.DAILY_USE,
        "daily_use": UseCase.DAILY_USE,
        "content creation": UseCase.CONTENT_CREATION,
        "content_creation": UseCase.CONTENT_CREATION,
    }
    key = value.lower().strip()
    if key not in mapping:
        raise ValidationError("Invalid use case selection", field="use_case")
    return mapping[key]


def validate_brand(value: str) -> BrandName:
    """Validate brand selection."""
    mapping = {b.value: b for b in BrandName}
    mapping.update(
        {
            "apple": BrandName.APPLE,
            "samsung": BrandName.SAMSUNG,
            "xiaomi": BrandName.XIAOMI,
            "google": BrandName.GOOGLE,
            "nothing": BrandName.NOTHING,
            "no preference": BrandName.NO_PREFERENCE,
        }
    )
    key = value.lower().strip()
    if key not in mapping:
        raise ValidationError("Invalid brand selection", field="brand")
    return mapping[key]


def validate_yes_no(value: str) -> bool:
    """Parse yes/no boolean input."""
    normalized = value.lower().strip()
    if normalized in ("yes", "y", "true", "✅ yes"):
        return True
    if normalized in ("no", "n", "false", "❌ no"):
        return False
    raise ValidationError("Please answer Yes or No", field="boolean")
