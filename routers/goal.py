from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependenices import get_current_user
from core.acl import verify_goal_ownership
from core.rate_limit import check_rate_limit
from core.audit import log_access
from db.session import get_db
from schemas.goal import GoalBasketSelect, GoalCreate, GoalOut, SipPlanOut
from services.goal_service import (
    create_goal_for_user,
    get_goals_for_user,
    get_sip_plan_for_goal,
    set_selected_basket_for_goal,
)

router = APIRouter(prefix="/goals", tags=["goals"])

@router.post("", response_model=GoalOut)
async def create_goal(
    payload: GoalCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new goal for the logged-in user"""
    goal = await create_goal_for_user(payload, user_id, db)
    await log_access(user_id, "CREATE", "goal", goal.id, db)
    return goal


@router.get("/me", response_model=list[GoalOut])
async def get_user_goals(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all goals for the logged-in user"""
    goals = await get_goals_for_user(user_id, db)
    await log_access(user_id, "READ", "goal", None, db)
    return goals


@router.get("/{goal_id}/sip-plan", response_model=SipPlanOut)
async def get_goal_sip_plan(
    goal_id: UUID,
    return_rate: Decimal = Query(default=Decimal("12.0"), ge=Decimal("0.1"), le=Decimal("50.0")),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership and rate limit
    await verify_goal_ownership(goal_id, user_id, db)
    await check_rate_limit(user_id)
    
    # Get SIP plan
    sip_plan = await get_sip_plan_for_goal(
        goal_id=goal_id,
        user_id=user_id,
        return_rate=return_rate,
        db=db,
    )
    
    # Log access
    await log_access(user_id, "READ", "sip_plan", goal_id, db)
    return sip_plan


@router.patch("/{goal_id}", response_model=GoalOut)
async def select_goal_basket(
    goal_id: UUID,
    payload: GoalBasketSelect,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    await verify_goal_ownership(goal_id, user_id, db)
    
    # Update basket
    goal = await set_selected_basket_for_goal(
        goal_id=goal_id,
        user_id=user_id,
        selected_basket=payload.selected_basket,
        db=db,
    )
    
    # Log access
    await log_access(user_id, "UPDATE", "goal", goal_id, db)
    return goal
