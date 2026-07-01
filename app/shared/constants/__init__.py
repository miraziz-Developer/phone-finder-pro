MESSAGE_SEPARATOR = "━━━━━━━━━━━━━━━━━━━━"
RAM_OPTIONS: tuple[int, ...] = (4, 6, 8, 12, 16)
STORAGE_OPTIONS: tuple[int, ...] = (64, 128, 256, 512, 1024)
REDIS_KEY_RATE_LIMIT = "rate_limit"


def get_page_size() -> int:
    from app.core.config import get_settings

    return get_settings().pagination_page_size


def get_comparison_max() -> int:
    from app.core.config import get_settings

    return get_settings().comparison_max_phones


def get_max_search_results() -> int:
    from app.core.config import get_settings

    return get_settings().pagination_max_page_size
