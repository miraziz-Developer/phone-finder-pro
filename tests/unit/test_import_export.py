import json

import pytest

from app.application.services.phone_import_export import (
    PhoneImportExportService,
    validate_phone_row,
)
from app.shared.exceptions import ValidationError


def test_validate_phone_row() -> None:
    row = validate_phone_row({"name": "Test", "brand": "samsung", "price": "599"})
    assert row["currency"] == "USD"
    assert row["price"] == 599


def test_validate_missing_name() -> None:
    with pytest.raises(ValidationError):
        validate_phone_row({"brand": "apple", "price": "999"})


def test_parse_json() -> None:
    data = json.dumps([{"name": "Phone A", "brand": "google", "price": "499"}])
    rows = PhoneImportExportService().parse_json(data.encode())
    assert len(rows) == 1


def test_parse_csv() -> None:
    content = b"name,brand,price,cpu\nPixel 9,google,899,Tensor\n"
    rows = PhoneImportExportService().parse_csv(content)
    assert rows[0]["name"] == "Pixel 9"


def test_export_csv() -> None:
    rows = [{"name": "Test", "brand": "apple", "price": "999"}]
    out = PhoneImportExportService().export_csv(rows)
    assert b"Test" in out
