"""Custom bot filters."""

from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.core.config import get_settings
from app.core.security.access import is_admin


class IsAdminFilter(BaseFilter):
    """Filter messages from admin users only."""

    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False
        return is_admin(message.from_user.id, get_settings())
