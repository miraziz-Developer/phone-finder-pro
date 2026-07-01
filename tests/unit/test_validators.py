import pytest

from app.application.validators import (
    validate_brand,
    validate_budget,
    validate_ram,
    validate_storage,
    validate_use_case,
    validate_yes_no,
)
from app.shared.enums import BrandName, UseCase
from app.shared.exceptions import ValidationError


def test_validate_budget_single_amount() -> None:
    min_b, max_b = validate_budget("800")
    assert float(max_b) == 800.0
    assert float(min_b) == pytest.approx(680.0)


def test_validate_budget_range() -> None:
    min_b, max_b = validate_budget("600-900")
    assert float(min_b) == 600.0
    assert float(max_b) == 900.0


def test_validate_budget_invalid() -> None:
    with pytest.raises(ValidationError):
        validate_budget("not-a-number")


def test_validate_ram_valid() -> None:
    assert validate_ram("8 GB") == 8


def test_validate_ram_invalid() -> None:
    with pytest.raises(ValidationError):
        validate_ram("3 GB")


def test_validate_storage_valid() -> None:
    assert validate_storage("256 GB") == 256


def test_validate_use_case() -> None:
    assert validate_use_case("Gaming") == UseCase.GAMING


def test_validate_brand() -> None:
    assert validate_brand("Apple") == BrandName.APPLE


def test_validate_yes_no() -> None:
    assert validate_yes_no("Yes") is True
    assert validate_yes_no("No") is False
