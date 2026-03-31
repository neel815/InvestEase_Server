"""
Centralized Access Control Layer for InvestEase

Provides reusable permission verification utilities to enforce user ownership
and role-based access across all resources.
"""

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.goal import Goal
from models.recommendation import Recommendation


async def verify_goal_ownership(
    goal_id: UUID,
    user_id: str,
    db: AsyncSession,
) -> Goal:
    """
    Verify that a goal belongs to the current user.
    
    Args:
        goal_id: The goal to verify ownership of
        user_id: The current user's ID (from JWT token)
        db: Database session
        
    Returns:
        The Goal object if ownership is verified
        
    Raises:
        HTTPException 403: If goal doesn't exist or doesn't belong to user
    """
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == UUID(user_id))
    )
    goal = result.scalar_one_or_none()
    
    if goal is None:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this goal"
        )
    
    return goal


async def verify_recommendation_ownership(
    recommendation_id: UUID,
    user_id: str,
    db: AsyncSession,
) -> Recommendation:
    """
    Verify that a recommendation belongs to a goal owned by the current user.
    
    Args:
        recommendation_id: The recommendation to verify ownership of
        user_id: The current user's ID (from JWT token)
        db: Database session
        
    Returns:
        The Recommendation object if ownership is verified
        
    Raises:
        HTTPException 403: If recommendation doesn't exist or doesn't belong to user
    """
    result = await db.execute(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == UUID(user_id)
        )
    )
    recommendation = result.scalar_one_or_none()
    
    if recommendation is None:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this recommendation"
        )
    
    return recommendation


async def require_mode(
    allowed_modes: list[str],
    goal_id: UUID,
    user_id: str,
    db: AsyncSession,
) -> Goal:
    """
    Verify goal ownership and check that goal's investment mode is in allowed list.
    
    Args:
        allowed_modes: List of allowed investment modes (e.g., ['autopilot', 'manual'])
        goal_id: The goal to check
        user_id: The current user's ID (from JWT token)
        db: Database session
        
    Returns:
        The Goal object if ownership and mode are verified
        
    Raises:
        HTTPException 403: If goal doesn't belong to user or mode is not allowed
    """
    # First verify ownership
    goal = await verify_goal_ownership(goal_id, user_id, db)
    
    # Then check investment mode
    if goal.investment_mode not in allowed_modes:
        raise HTTPException(
            status_code=403,
            detail=f"This action is not available in {goal.investment_mode} mode"
        )
    
    return goal
