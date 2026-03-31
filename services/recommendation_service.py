from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.recommendation_rules import build_recommendation_baskets
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

    return GoalRecommendationsOut(
        goal_id=goal.id,
        recommended_at=recommendation_payload["recommended_at"],
        baskets=recommendation_payload["baskets"],
    )
