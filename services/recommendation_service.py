from uuid import UUID
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.goal import Goal
from schemas.recommendation import GoalRecommendationsOut
from services.recommendation_engine import RecommendationEngine


async def get_goal_recommendations(goal_id: UUID, user_id: str, db: AsyncSession) -> GoalRecommendationsOut:
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == UUID(user_id))
    )
    goal = result.scalar_one_or_none()

    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Build recommendations from hardcoded sample mutual funds
    recommendation_payload = await RecommendationEngine.build_recommendation_baskets_dynamic(
        db=db,
        goal_type=goal.goal_type,
        investment_mode=goal.investment_mode,
        target_date=goal.target_date,  # Pass target date for horizon calculation
        use_real_data=True,  # (parameter ingored - always uses hardcoded data)
        as_of_date=datetime.utcnow(),
    )

    return GoalRecommendationsOut(
        goal_id=goal.id,
        recommended_at=recommendation_payload["recommended_at"],
        baskets=recommendation_payload["baskets"],
        horizon=recommendation_payload.get("horizon"),
        horizon_note=recommendation_payload.get("horizon_note"),
    )
