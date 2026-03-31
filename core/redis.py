"""
Redis client for token blacklist, caching, and rate limiting.
"""

import json
from typing import Any, Optional
import redis.asyncio as redis
from core.config import settings

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or initialize the Redis client."""
    global _redis_client
    if _redis_client is None:
        # Construct REDIS_URL from config settings
        redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        _redis_client = await redis.from_url(redis_url, decode_responses=True)
    return _redis_client


async def blacklist_token(token: str, expiry_seconds: int) -> None:
    """
    Blacklist a token (add to Redis with TTL).
    
    Args:
        token: The JWT token to blacklist
        expiry_seconds: Seconds until the token expires (for TTL)
    """
    client = await get_redis_client()
    key = f"token_blacklist:{token}"
    await client.setex(key, expiry_seconds, "1")


async def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.
    
    Args:
        token: The JWT token to check
        
    Returns:
        True if the token is blacklisted, False otherwise
    """
    client = await get_redis_client()
    key = f"token_blacklist:{token}"
    return await client.exists(key) > 0


async def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    """
    Set a value in Redis cache with TTL.
    
    Args:
        key: The cache key
        value: The value to cache (will be JSON encoded)
        ttl_seconds: Time to live in seconds (default 1 hour)
    """
    client = await get_redis_client()
    serialized_value = json.dumps(value, default=str)
    await client.setex(key, ttl_seconds, serialized_value)


async def cache_get(key: str) -> Optional[Any]:
    """
    Get a value from Redis cache.
    
    Args:
        key: The cache key
        
    Returns:
        The cached value (JSON decoded) or None if not found/expired
    """
    client = await get_redis_client()
    value = await client.get(key)
    if value is None:
        return None
    return json.loads(value)


async def cache_delete(key: str) -> None:
    """
    Delete a key from Redis cache.
    
    Args:
        key: The cache key to delete
    """
    client = await get_redis_client()
    await client.delete(key)


async def cleanup_redis() -> None:
    """Close Redis connection (call on app shutdown)."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
