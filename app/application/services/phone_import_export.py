"""Phone import/export service — CSV, Excel, JSON."""

import csv
import io
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.shared.exceptions import ValidationError

logger = get_logger(__name__)

# Canonical import column mapping (case-insensitive)
IMPORT_COLUMNS = {
    "name": "name",
    "model": "name",
    "brand": "brand",
    "price": "price",
    "cpu": "cpu",
    "processor": "cpu",
    "gpu": "gpu",
    "ram_gb": "ram_gb",
    "ram": "ram_gb",
    "storage_gb": "storage_gb",
    "storage": "storage_gb",
    "battery_mah": "battery_mah",
    "battery": "battery_mah",
    "charging_watts": "charging_watts",
    "charging": "charging_watts",
    "camera_main_mp": "camera_main_mp",
    "camera": "camera_main_mp",
    "camera_front_mp": "camera_front_mp",
    "front_camera": "camera_front_mp",
    "model_year": "model_year",
    "release_year": "model_year",
    "description": "description",
    "advantages": "advantages",
    "disadvantages": "disadvantages",
    "has_5g": "has_5g",
    "5g": "has_5g",
    "has_nfc": "has_nfc",
    "nfc": "has_nfc",
    "has_wireless_charging": "has_wireless_charging",
    "wireless_charging": "has_wireless_charging",
    "has_esim": "has_esim",
    "esim": "has_esim",
    "display_type": "display_type",
    "display": "display_type",
    "refresh_rate_hz": "refresh_rate_hz",
    "refresh_rate": "refresh_rate_hz",
    "display_resolution": "display_resolution",
    "resolution": "display_resolution",
    "display_size_inches": "display_size_inches",
    "os_version": "os_version",
    "android_version": "os_version",
    "ip_rating": "ip_rating",
    "waterproof": "ip_rating",
    "weight_grams": "weight_grams",
    "weight": "weight_grams",
    "dimensions": "dimensions",
    "sim_type": "sim_type",
    "bluetooth": "bluetooth",
    "wifi": "wifi",
    "usb_type": "usb_type",
    "colors": "colors",
    "image_url": "image_url",
    "images": "images",
    "performance_score": "performance_score",
    "camera_score": "camera_score",
    "battery_score": "battery_score",
    "display_score": "display_score",
    "original_price": "original_price",
    "discount_percent": "discount_percent",
    "slug": "slug",
    "category": "category",
}


@dataclass
class ImportResult:
    """Result of a bulk import operation."""

    total_rows: int
    imported: int
    skipped: int
    duplicates: int
    errors: list[str]


def _normalize_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Map raw import row to canonical field names."""
    normalized: dict[str, Any] = {}
    for key, value in raw.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        canonical = IMPORT_COLUMNS.get(key.lower().strip().replace(" ", "_"))
        if canonical:
            normalized[canonical] = value
    return normalized


def _parse_bool(value: Any) -> bool:
    """Parse boolean from various string formats."""
    if isinstance(value, bool):
        return value
    return str(value).lower().strip() in ("true", "yes", "1", "y", "✅")


def _parse_list(value: Any) -> list[str]:
    """Parse comma/semicolon separated list."""
    if isinstance(value, list):
        return [str(v).strip() for v in value if v]
    return [p.strip() for p in str(value).replace(";", ",").split(",") if p.strip()]


def validate_phone_row(row: dict[str, Any], settings: Settings | None = None) -> dict[str, Any]:
    """
    Validate and normalize a single phone import row.

    Raises:
        ValidationError: If required fields are missing or invalid.
    """
    cfg = settings or get_settings()
    data = _normalize_row(row)

    if not data.get("name"):
        raise ValidationError("Missing required field: name", field="name")
    if not data.get("brand"):
        raise ValidationError("Missing required field: brand", field="brand")

    try:
        price = Decimal(str(data.get("price", 0)).replace("$", "").replace(",", ""))
    except InvalidOperation as exc:
        raise ValidationError("Invalid price value", field="price") from exc

    if price <= 0:
        raise ValidationError("Price must be positive (USD)", field="price")

    slug = data.get("slug") or str(data["name"]).lower().replace(" ", "-").replace("/", "-")

    return {
        "name": str(data["name"]).strip(),
        "brand": str(data["brand"]).strip().lower(),
        "slug": str(slug).strip().lower(),
        "price": price,
        "currency": cfg.default_currency,
        "cpu": str(data.get("cpu", "Unknown")).strip(),
        "gpu": str(data["gpu"]).strip() if data.get("gpu") else None,
        "ram_gb": int(data.get("ram_gb", 8)),
        "storage_gb": int(data.get("storage_gb", 128)),
        "battery_mah": int(data.get("battery_mah", 4000)),
        "charging_watts": int(data["charging_watts"]) if data.get("charging_watts") else None,
        "camera_main_mp": float(data.get("camera_main_mp", 48)),
        "camera_front_mp": float(data.get("camera_front_mp", 12)),
        "model_year": int(data.get("model_year", 2025)),
        "description": str(data["description"]) if data.get("description") else None,
        "advantages": _parse_list(data.get("advantages", [])),
        "disadvantages": _parse_list(data.get("disadvantages", [])),
        "performance_score": float(data.get("performance_score", 70)),
        "camera_score": float(data.get("camera_score", 70)),
        "battery_score": float(data.get("battery_score", 70)),
        "display_score": float(data.get("display_score", 70)),
        "original_price": Decimal(str(data["original_price"]))
        if data.get("original_price")
        else None,
        "discount_percent": float(data["discount_percent"])
        if data.get("discount_percent")
        else None,
        "weight_grams": float(data["weight_grams"]) if data.get("weight_grams") else None,
        "dimensions": str(data["dimensions"]) if data.get("dimensions") else None,
        "colors": _parse_list(data.get("colors", [])),
        "category": str(data.get("category", "mid-range")).strip().lower(),
        "image_url": str(data["image_url"]) if data.get("image_url") else None,
        "images": _parse_list(data.get("images", [])),
        "features": {
            "has_5g": _parse_bool(data.get("has_5g", False)),
            "has_nfc": _parse_bool(data.get("has_nfc", False)),
            "has_wireless_charging": _parse_bool(data.get("has_wireless_charging", False)),
            "has_esim": _parse_bool(data.get("has_esim", False)),
            "has_amoled": _parse_bool(data.get("display_type", "AMOLED").upper() == "AMOLED"),
            "has_high_refresh": int(data.get("refresh_rate_hz", 60)) >= 90,
            "has_fingerprint": _parse_bool(data.get("has_fingerprint", True)),
            "refresh_rate_hz": int(data.get("refresh_rate_hz", 60)),
            "display_type": str(data.get("display_type", "AMOLED")),
            "display_size_inches": float(data.get("display_size_inches", 6.5)),
            "display_resolution": str(data.get("display_resolution", "2400x1080")),
            "ip_rating": str(data["ip_rating"]) if data.get("ip_rating") else None,
            "os_version": str(data.get("os_version", "")) or None,
            "sim_type": str(data["sim_type"]) if data.get("sim_type") else None,
            "bluetooth": str(data["bluetooth"]) if data.get("bluetooth") else None,
            "wifi": str(data["wifi"]) if data.get("wifi") else None,
            "usb_type": str(data["usb_type"]) if data.get("usb_type") else None,
            "stereo_speakers": _parse_bool(data.get("stereo_speakers", False)),
        },
    }


class PhoneImportExportService:
    """Parse and serialize phone catalog data."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def parse_csv(self, content: bytes) -> list[dict[str, Any]]:
        """Parse CSV bytes into list of validated phone dicts."""
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        if len(rows) > self._settings.import_max_rows:
            raise ValidationError(f"Max {self._settings.import_max_rows} rows allowed")
        return [validate_phone_row(row, self._settings) for row in rows]

    def parse_json(self, content: bytes) -> list[dict[str, Any]]:
        """Parse JSON array into validated phone dicts."""
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValidationError("JSON must be an array of phone objects")
        if len(data) > self._settings.import_max_rows:
            raise ValidationError(f"Max {self._settings.import_max_rows} rows allowed")
        return [validate_phone_row(item, self._settings) for item in data]

    def parse_excel(self, content: bytes) -> list[dict[str, Any]]:
        """Parse Excel bytes into validated phone dicts."""
        try:
            import openpyxl
        except ImportError as exc:
            raise ValidationError("openpyxl not installed") from exc

        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
        ws = wb.active
        if ws is None:
            raise ValidationError("Excel file has no active sheet")

        rows_iter = ws.iter_rows(values_only=True)
        headers = [str(h).strip() if h else "" for h in next(rows_iter)]
        raw_rows = []
        for row in rows_iter:
            raw_rows.append(dict(zip(headers, row, strict=False)))

        wb.close()
        if len(raw_rows) > self._settings.import_max_rows:
            raise ValidationError(f"Max {self._settings.import_max_rows} rows allowed")
        return [validate_phone_row(row, self._settings) for row in raw_rows]

    def export_json(self, phones: list[dict[str, Any]]) -> bytes:
        """Export phones to JSON bytes."""
        return json.dumps(phones, indent=2, default=str).encode()

    def export_csv(self, phones: list[dict[str, Any]]) -> bytes:
        """Export phones to CSV bytes."""
        if not phones:
            return b""
        output = io.StringIO()
        fieldnames = list(phones[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(phones)
        return output.getvalue().encode()
