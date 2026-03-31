"""
Celery tasks for caching and background jobs.
"""

from celery import shared_task
from services.mfapi_service import get_top_funds_by_category
from core.redis import cache_set


FUND_CATEGORIES = ["Large Cap", "Mid Cap", "Small Cap", "Debt", "Liquid", "Hybrid", "Sectoral"]


@shared_task
def cache_top_funds():
    """
    Daily Celery beat task that caches top funds for all categories.
    Runs once every 24 hours to refresh fund data.
    """
    import asyncio
    
    async def run_cache():
        for category in FUND_CATEGORIES:
            try:
                # Fetch top 3 funds for the category
                funds = await get_top_funds_by_category(category, top_n=3)
                
                # Store in Redis with 24-hour TTL
                cache_key = f"top_funds:{category}"
                await cache_set(cache_key, funds, ttl_seconds=86400)
                
                print(f"Cached {len(funds)} top funds for category '{category}'")
            except Exception as e:
                print(f"Error caching funds for category '{category}': {e}")
    
    asyncio.run(run_cache())
