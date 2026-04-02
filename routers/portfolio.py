from uuid import UUID
from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.dependenices import get_current_user
from core.acl import verify_goal_ownership, require_mode
from db.session import get_db
from models.sip_schedule import SIPSchedule
from models.portfolio_summary import PortfolioSummary
from models.goal import Goal
from schemas.sip import SIPConfirmIn, SIPScheduleOut

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


def calculate_next_sip_date(current_date: date, sip_day: int) -> date:
    """
    Calculate the next SIP due date based on current date and target sip_day.
    
    Handles edge cases where the target day doesn't exist in a month by using
    the last valid day of that month.
    
    Args:
        current_date: The reference date (typically today)
        sip_day: The day of month for SIP (1-31)
        
    Returns:
        The next occurrence of sip_day (or last day of month if sip_day > days in month)
    """
    def get_last_day_of_month(year: int, month: int) -> int:
        """Get the last day of a given month."""
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        return last_day.day
    
    # Try this month's sip_day
    last_day_this_month = get_last_day_of_month(current_date.year, current_date.month)
    target_day_this_month = min(sip_day, last_day_this_month)
    
    try:
        target_this_month = date(current_date.year, current_date.month, target_day_this_month)
        if current_date < target_this_month:
            return target_this_month
    except ValueError:
        pass
    
    # If today is on or after sip_day this month, use next month
    if current_date.month == 12:
        next_year = current_date.year + 1
        next_month = 1
    else:
        next_year = current_date.year
        next_month = current_date.month + 1
    
    last_day_next_month = get_last_day_of_month(next_year, next_month)
    target_day_next_month = min(sip_day, last_day_next_month)
    
    return date(next_year, next_month, target_day_next_month)


@router.post("/sip/confirm", response_model=SIPScheduleOut)
async def confirm_sip(
    payload: SIPConfirmIn,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Enforce ACL: only autopilot and copilot allowed
    await require_mode(["autopilot", "copilot"], payload.goal_id, user_id, db)

    # Calculate next SIP due date based on sip_day
    today = date.today()
    next_due = calculate_next_sip_date(today, payload.sip_day)

    new = SIPSchedule(
        user_id=UUID(user_id),
        goal_id=payload.goal_id,
        selected_basket=payload.selected_basket,
        monthly_amount=payload.monthly_amount,
        next_due_date=next_due,
        sip_day=payload.sip_day,
        status="active",
    )
    db.add(new)

    # Create portfolio summary row
    ps = PortfolioSummary(
        user_id=UUID(user_id),
        goal_id=payload.goal_id,
        total_invested=0,
        current_value=0,
    )
    db.add(ps)

    await db.commit()
    await db.refresh(new)

    return new


@router.get("/sip/schedule")
async def get_sip_schedules(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Return active SIP schedules for user with joined goal details
    q = select(SIPSchedule, Goal).join(Goal, SIPSchedule.goal_id == Goal.id).where(
        SIPSchedule.user_id == UUID(user_id), SIPSchedule.status == "active"
    )
    result = await db.execute(q)
    rows = result.all()

    schedules = []
    for sip, goal in rows:
        schedules.append({
            "sip": sip,
            "goal": goal,
        })

    return schedules


@router.patch("/sip/schedule/{sip_id}/pause")
async def pause_sip(sip_id: UUID, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = select(SIPSchedule).where(SIPSchedule.id == sip_id)
    res = await db.execute(q)
    sip = res.scalar_one_or_none()
    if sip is None:
        raise HTTPException(status_code=404, detail="SIP schedule not found")

    # Verify goal ownership
    await verify_goal_ownership(sip.goal_id, user_id, db)

    sip.status = "paused"
    db.add(sip)
    await db.commit()
    await db.refresh(sip)
    return {"status": "paused"}


@router.patch("/sip/schedule/{sip_id}/resume")
async def resume_sip(sip_id: UUID, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = select(SIPSchedule).where(SIPSchedule.id == sip_id)
    res = await db.execute(q)
    sip = res.scalar_one_or_none()
    if sip is None:
        raise HTTPException(status_code=404, detail="SIP schedule not found")

    # Verify goal ownership
    await verify_goal_ownership(sip.goal_id, user_id, db)

    sip.status = "active"
    db.add(sip)
    await db.commit()
    await db.refresh(sip)
    return {"status": "active"}


@router.get("/summary")
async def portfolio_summary(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Aggregate totals
    total_q = select(
        func.coalesce(func.sum(PortfolioSummary.total_invested), 0),
        func.coalesce(func.sum(PortfolioSummary.current_value), 0),
    ).where(PortfolioSummary.user_id == UUID(user_id))
    total_res = await db.execute(total_q)
    total_invested_sum, current_value_sum = total_res.fetchone()

    # Overall return percentage
    overall_return_pct = None
    if total_invested_sum and float(total_invested_sum) != 0:
        overall_return_pct = (float(current_value_sum) - float(total_invested_sum)) / float(total_invested_sum) * 100

    # Count active goals
    count_q = select(func.count(func.distinct(PortfolioSummary.goal_id))).where(PortfolioSummary.user_id == UUID(user_id))
    cnt = (await db.execute(count_q)).scalar_one()

    # Next SIP due date
    next_q = select(func.min(SIPSchedule.next_due_date)).where(SIPSchedule.user_id == UUID(user_id), SIPSchedule.status == "active")
    next_due = (await db.execute(next_q)).scalar_one()

    # Per-goal breakdown
    breakdown_q = select(PortfolioSummary, Goal).join(Goal, PortfolioSummary.goal_id == Goal.id).where(PortfolioSummary.user_id == UUID(user_id))
    breakdown_res = await db.execute(breakdown_q)
    rows = breakdown_res.all()
    per_goal = []
    for ps, goal in rows:
        target = float(goal.target_amount)
        current = float(ps.current_value)
        progress = None
        if target and target > 0:
            progress = (current / target) * 100

        per_goal.append({
            "goal_id": goal.id,
            "goal_type": goal.goal_type,
            "goal_name": getattr(goal, 'name', None),
            "target_amount": float(goal.target_amount),
            "total_invested": float(ps.total_invested),
            "current_value": float(ps.current_value),
            "progress_percentage": progress,
            "selected_basket": goal.selected_basket,
        })

    return {
        "total_invested": float(total_invested_sum or 0),
        "current_value": float(current_value_sum or 0),
        "overall_return_percentage": overall_return_pct,
        "active_goals_count": cnt,
        "next_sip_due": next_due,
        "per_goal": per_goal,
    }
