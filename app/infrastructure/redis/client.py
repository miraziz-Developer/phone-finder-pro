"""Redis client factory."""

from redis.asyncio import Redis

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis_client: Redis | None = None


async def get_redis(settings: Settings | None = None) -> Redis:
    """Return or create the global Redis client."""
    global _redis_client
    if _redis_client is None:
        cfg = settings or get_settings()
        _redis_client = Redis.from_url(
            cfg.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("redis_client_initialized", host=cfg.redis_host)
    return _redis_client


async def close_redis() -> None:
    """Close the global Redis connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("redis_client_closed")
