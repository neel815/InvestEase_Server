from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.goal import Goal
from schemas.goal import GoalCreate, SipPlanOut, YearProjection


_HUNDRED = Decimal("100")
_TWELVE = Decimal("12")
_ZERO = Decimal("0")
_ONE = Decimal("1")
_TWO_DP = Decimal("0.01")


def _months_until_target(target_date: date) -> int:
    today = date.today()
    months = (target_date.year - today.year) * 12 + (target_date.month - today.month)
    if target_date.day > today.day:
        months += 1
    return max(months, 1)


def _round2(value: Decimal) -> Decimal:
    return value.quantize(_TWO_DP, rounding=ROUND_HALF_UP)


async def create_goal_for_user(payload: GoalCreate, user_id: str, db: AsyncSession) -> Goal:
    goal = Goal(
        user_id=UUID(user_id),
        goal_type=payload.goal_type,
        target_amount=payload.target_amount,
        target_date=payload.target_date,
        investment_mode=payload.investment_mode,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


async def get_goals_for_user(user_id: str, db: AsyncSession) -> list[Goal]:
    result = await db.execute(select(Goal).where(Goal.user_id == UUID(user_id)))
    return list(result.scalars().all())


async def set_selected_basket_for_goal(
    goal_id: UUID,
    user_id: str,
    selected_basket: str,
    db: AsyncSession,
) -> Goal:
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == UUID(user_id))
    )
    goal = result.scalar_one_or_none()

    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    goal.selected_basket = selected_basket
    await db.commit()
    await db.refresh(goal)
    return goal


async def get_sip_plan_for_goal(
    goal_id: UUID,
    user_id: str,
    return_rate: Decimal,
    db: AsyncSession,
) -> SipPlanOut:
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == UUID(user_id))
    )
    goal = result.scalar_one_or_none()

    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    n = _months_until_target(goal.target_date)
    fv = Decimal(goal.target_amount)
    monthly_rate = (return_rate / _HUNDRED) / _TWELVE

    if monthly_rate == _ZERO:
        monthly_sip = fv / Decimal(n)
    else:
        denominator = (_ONE + monthly_rate) ** n - _ONE
        if denominator <= _ZERO:
            raise HTTPException(status_code=400, detail="Unable to calculate SIP plan")
        monthly_sip = fv * monthly_rate / denominator

    total_invested = monthly_sip * Decimal(n)
    estimated_returns = fv - total_invested

    total_years = max(1, ceil(n / 12))
    year_by_year: list[YearProjection] = []

    for year in range(1, total_years + 1):
        months = min(year * 12, n)
        if monthly_rate == _ZERO:
            projected_value = monthly_sip * Decimal(months)
        else:
            projected_value = monthly_sip * (((_ONE + monthly_rate) ** months - _ONE) / monthly_rate)

        year_by_year.append(YearProjection(year=year, projected_value=_round2(projected_value)))

    return SipPlanOut(
        monthly_sip=_round2(monthly_sip),
        total_invested=_round2(total_invested),
        estimated_returns=_round2(estimated_returns),
        year_by_year=year_by_year,
    )
