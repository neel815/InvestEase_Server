"""
Rate limiting for computationally expensive operations.

Implements per-user rate limiting for SIP calculation endpoints
to prevent abuse from rapid slider movements.
"""

import time
from fastapi import HTTPException
from collections import defaultdict

# In-memory rate limit counters: {user_id: [(timestamp, count)]}
_rate_limit_counters = defaultdict(list)

# Configuration
RATE_LIMIT_MAX_REQUESTS = 30  # Max requests
RATE_LIMIT_WINDOW_SECONDS = 60  # Per minute


async def check_rate_limit(user_id: str) -> None:
    """
    Check if a user has exceeded rate limit for SIP calculations.
    
    Args:
        user_id: The user's ID (from JWT)
        
    Raises:
        HTTPException 429: If rate limit exceeded
    """
    current_time = time.time()
    window_start = current_time - RATE_LIMIT_WINDOW_SECONDS
    
    # Get or initialize counter for this user
    if user_id not in _rate_limit_counters:
        _rate_limit_counters[user_id] = []
    
    # Clean old timestamps outside the window
    _rate_limit_counters[user_id] = [
        ts for ts in _rate_limit_counters[user_id]
        if ts > window_start
    ]
    
    # Check if limit exceeded
    if len(_rate_limit_counters[user_id]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many requests, slow down"
        )
    
    # Add current timestamp
    _rate_limit_counters[user_id].append(current_time)


def reset_rate_limit(user_id: str) -> None:
    """Reset rate limit counter for a specific user (for testing)."""
    if user_id in _rate_limit_counters:
        del _rate_limit_counters[user_id]
