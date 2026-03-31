"""
Rate limiting for computationally expensive operations.

Implements per-user rate limiting using Redis for SIP calculation endpoints
to prevent abuse from rapid slider movements. Persists across restarts and works across instances.
"""

from fastapi import HTTPException
from core.redis import get_redis_client

# Configuration
RATE_LIMIT_MAX_REQUESTS = 30  # Max requests
RATE_LIMIT_WINDOW_SECONDS = 60  # Per minute


async def check_rate_limit(user_id: str) -> None:
    """
    Check if a user has exceeded rate limit for SIP calculations using Redis.
    
    Args:
        user_id: The user's ID (from JWT)
        
    Raises:
        HTTPException 429: If rate limit exceeded
    """
    client = await get_redis_client()
    key = f"rate_limit:{user_id}:sip_calculation"
    
    # Get current count
    current_count = await client.get(key)
    count = int(current_count) if current_count else 0
    
    # Check if limit exceeded
    if count >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many requests, slow down"
        )
    
    # Increment counter with TTL
    pipe = client.pipeline()
    pipe.incr(key)
    pipe.expire(key, RATE_LIMIT_WINDOW_SECONDS)
    await pipe.execute()


def reset_rate_limit(user_id: str) -> None:
    """Reset rate limit counter for a specific user (for testing)."""
    # Note: This is async in reality but kept for API compatibility
    # Call with asyncio: await reset_rate_limit_async(user_id)
    pass


async def reset_rate_limit_async(user_id: str) -> None:
    """Reset rate limit counter for a specific user (async version for testing)."""
    client = await get_redis_client()
    key = f"rate_limit:{user_id}:sip_calculation"
    await client.delete(key)

