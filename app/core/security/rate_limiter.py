"""Redis-backed rate limiter using sliding window counter."""

import time

from redis.asyncio import Redis

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.shared.constants import REDIS_KEY_RATE_LIMIT
from app.shared.exceptions import RateLimitExceededError

logger = get_logger(__name__)


class RateLimiter:
    """Sliding window rate limiter backed by Redis."""

    def __init__(
        self,
        redis: Redis,
        settings: Settings | None = None,
    ) -> None:
        self._redis = redis
        self._settings = settings or get_settings()

    def _key(self, user_id: int) -> str:
        """Build Redis key for user rate limit bucket."""
        return f"{REDIS_KEY_RATE_LIMIT}:{user_id}"

    async def check(self, user_id: int) -> None:
        """
        Check and increment rate limit counter for user.

        Raises:
            RateLimitExceededError: If the user exceeds the rate limit.
        """
        key = self._key(user_id)
        window = self._settings.rate_limit_window_seconds
        limit = self._settings.rate_limit_requests
        now = time.time()
        window_start = now - window

        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window)
        results = await pipe.execute()

        request_count: int = results[2]
        if request_count > limit:
            logger.warning(
                "rate_limit_exceeded",
                user_id=user_id,
                count=request_count,
                limit=limit,
            )
            raise RateLimitExceededError(retry_after=window)

    async def reset(self, user_id: int) -> None:
        """Reset rate limit counter for a user."""
        await self._redis.delete(self._key(user_id))
