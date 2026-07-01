"""Admin access control."""

from app.core.config import Settings, get_settings


def is_admin(user_id: int, settings: Settings | None = None) -> bool:
    """Check if the given Telegram user ID is an admin."""
    cfg = settings or get_settings()
    return user_id in cfg.admin_ids
