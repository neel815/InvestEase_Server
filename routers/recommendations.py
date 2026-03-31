from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependenices import get_current_user
from core.acl import verify_goal_ownership
from core.audit import log_access
from core.redis import cache_get, cache_set
from db.session import get_db
from schemas.recommendation import GoalRecommendationsOut
from services.recommendation_service import get_goal_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{goal_id}", response_model=GoalRecommendationsOut)
async def recommendations_for_goal(
    goal_id: UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership before generating/returning recommendations
    try:
        await verify_goal_ownership(goal_id, user_id, db)
    except HTTPException as e:
        # Log denied access attempt
        await log_access(user_id, "DENIED", "recommendation", goal_id, db)
        raise e
    
    # Check cache first
    cache_key = f"recommendations:{goal_id}"
    cached = await cache_get(cache_key)
    if cached:
        # Log access
        await log_access(user_id, "READ", "recommendation", goal_id, db)
        return cached
    
    # Get recommendations from DB
    recommendations = await get_goal_recommendations(goal_id=goal_id, user_id=user_id, db=db)
    
    # Cache the result with 1 hour TTL
    await cache_set(cache_key, recommendations.dict(), ttl_seconds=3600)
    
    # Log access
    await log_access(user_id, "READ", "recommendation", goal_id, db)
    return recommendations
