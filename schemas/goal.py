from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime

class GoalCreate(BaseModel):
    goal_type: str  # retirement, house, education, wealth
    target_amount: Decimal
    target_date: date
    investment_mode: str  # autopilot, copilot, manual

class GoalOut(BaseModel):
    id: UUID
    user_id: UUID
    goal_type: str
    target_amount: Decimal
    target_date: date
    investment_mode: str
    selected_basket: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: lambda value: float(value)},
    )


class YearProjection(BaseModel):
    year: int
    projected_value: Decimal


class SipPlanOut(BaseModel):
    monthly_sip: Decimal
    total_invested: Decimal
    estimated_returns: Decimal
    year_by_year: list[YearProjection]

    model_config = ConfigDict(json_encoders={Decimal: lambda value: float(value)})


class GoalBasketSelect(BaseModel):
    selected_basket: Literal["conservative", "moderate", "aggressive"]
