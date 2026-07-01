"""Phone domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class PhoneFeatures:
    """Technical features and capabilities of a phone."""

    id: int | None
    phone_id: int
    has_5g: bool
    has_nfc: bool
    has_wireless_charging: bool
    has_esim: bool
    has_amoled: bool
    has_high_refresh: bool
    refresh_rate_hz: int
    display_size_inches: float
    display_resolution: str
    ip_rating: str | None
    os_version: str | None
    has_fingerprint: bool = True
    display_type: str = "AMOLED"
    sim_type: str | None = None
    bluetooth: str | None = None
    wifi: str | None = None
    usb_type: str | None = None
    stereo_speakers: bool = False


@dataclass(slots=True)
class PhoneImage:
    """Image associated with a phone."""

    id: int | None
    phone_id: int
    url: str
    is_primary: bool
    sort_order: int


@dataclass(slots=True)
class Phone:
    """Smartphone product entity."""

    id: int | None
    brand_id: int
    category_id: int
    name: str
    slug: str
    model_year: int
    price: Decimal
    currency: str
    cpu: str
    gpu: str | None
    ram_gb: int
    storage_gb: int
    battery_mah: int
    camera_main_mp: float
    camera_ultra_mp: float | None
    camera_tele_mp: float | None
    camera_front_mp: float
    performance_score: float
    camera_score: float
    battery_score: float
    display_score: float
    advantages: list[str] = field(default_factory=list)
    disadvantages: list[str] = field(default_factory=list)
    is_active: bool = True
    view_count: int = 0
    recommendation_count: int = 0
    original_price: Decimal | None = None
    discount_percent: float | None = None
    description: str | None = None
    charging_watts: int | None = None
    rating_avg: float = 0.0
    review_count: int = 0
    weight_grams: float | None = None
    dimensions: str | None = None
    colors: list[str] = field(default_factory=list)
    release_date: None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # Loaded relations (optional)
    brand_name: str | None = None
    category_name: str | None = None
    features: PhoneFeatures | None = None
    images: list[PhoneImage] = field(default_factory=list)

    @property
    def camera_description(self) -> str:
        """Human-readable camera specification."""
        parts = [f"{self.camera_main_mp:.0f}MP main"]
        if self.camera_ultra_mp:
            parts.append(f"{self.camera_ultra_mp:.0f}MP ultra-wide")
        if self.camera_tele_mp:
            parts.append(f"{self.camera_tele_mp:.0f}MP telephoto")
        parts.append(f"{self.camera_front_mp:.0f}MP front")
        return ", ".join(parts)

    @property
    def primary_image_url(self) -> str | None:
        """Return the primary image URL if available."""
        for img in self.images:
            if img.is_primary:
                return img.url
        return self.images[0].url if self.images else None
