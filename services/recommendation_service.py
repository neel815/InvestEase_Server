from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.recommendation_rules import build_recommendation_baskets
from core.redis import cache_get
from services.mfapi_service import get_top_funds_by_category
from models.goal import Goal
from schemas.recommendation import GoalRecommendationsOut


async def get_goal_recommendations(goal_id: UUID, user_id: str, db: AsyncSession) -> GoalRecommendationsOut:
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == UUID(user_id))
    )
    goal = result.scalar_one_or_none()

    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    recommendation_payload = build_recommendation_baskets(
        goal_type=goal.goal_type,
        investment_mode=goal.investment_mode,
    )
    
    # Resolve categories to actual fund data from MFAPI
    baskets = []
    for basket_info in recommendation_payload["baskets"]:
        basket_type = basket_info["basket_type"]
        categories = basket_info.get("categories", [])
        
        # Collect funds from all categories in this basket
        basket_funds = []
        for category in categories:
            try:
                # Try to get from Redis cache first
                cache_key = f"top_funds:{category}"
                cached_funds = await cache_get(cache_key)
                
                if cached_funds:
                    basket_funds.extend(cached_funds)
                else:
                    # Cache miss - fetch directly from MFAPI
                    funds = await get_top_funds_by_category(category, top_n=3)
                    basket_funds.extend(funds)
            except Exception as e:
                # Log error but don't fail - try next category
                print(f"Error fetching funds for category '{category}': {e}")
                continue
        
        baskets.append(
            {
                "basket_type": basket_type,
                "recommended": basket_info["recommended"],
                "funds": basket_funds,
            }
        )

    return GoalRecommendationsOut(
        goal_id=goal.id,
        recommended_at=recommendation_payload["recommended_at"],
        baskets=baskets,
    )

