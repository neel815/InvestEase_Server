from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from datetime import date, datetime


class SIPConfirmIn(BaseModel):
    goal_id: UUID
    selected_basket: str
    monthly_amount: Decimal
    sip_day: int = Field(default=1, ge=1, le=31, description="Day of month for SIP (1-31). For months with fewer days, SIP schedules on last day.")


class SIPScheduleOut(BaseModel):
    id: UUID
    user_id: UUID
    goal_id: UUID
    selected_basket: str
    monthly_amount: Decimal
    next_due_date: date
    sip_day: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: lambda v: float(v)}


class PortfolioSummaryOut(BaseModel):
    id: UUID
    user_id: UUID
    goal_id: UUID
    total_invested: Decimal
    current_value: Decimal
    last_updated: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: lambda v: float(v)}
