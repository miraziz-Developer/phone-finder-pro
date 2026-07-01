"""Brand domain entity."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Brand:
    """Smartphone manufacturer."""

    id: int | None
    name: str
    slug: str
    logo_url: str | None
    is_active: bool
    created_at: datetime | None = None
