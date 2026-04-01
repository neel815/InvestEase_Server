from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import date, datetime


class SIPConfirmIn(BaseModel):
    goal_id: UUID
    selected_basket: str
    monthly_amount: Decimal


class SIPScheduleOut(BaseModel):
    id: UUID
    user_id: UUID
    goal_id: UUID
    selected_basket: str
    monthly_amount: Decimal
    next_due_date: date
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {Decimal: lambda v: float(v)}


class PortfolioSummaryOut(BaseModel):
    id: UUID
    user_id: UUID
    goal_id: UUID
    total_invested: Decimal
    current_value: Decimal
    last_updated: datetime

    class Config:
        orm_mode = True
        json_encoders = {Decimal: lambda v: float(v)}
