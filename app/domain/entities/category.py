"""Category domain entity."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Category:
    """Phone category (flagship, mid-range, budget)."""

    id: int | None
    name: str
    slug: str
    description: str | None
    created_at: datetime | None = None
