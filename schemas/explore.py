from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime


class FundSearchResultOut(BaseModel):
    scheme_code: str
    scheme_name: str


class FundDetailsOut(BaseModel):
    scheme_code: str
    scheme_name: str
    category: str
    current_nav: Optional[float] = None
    nav_history: List[Dict[str, str]]  # [{"date": "01-04-2026", "nav": "100.50"}]


class ExploreInvestIn(BaseModel):
    goal_id: UUID
    scheme_code: str
    scheme_name: str
    category: str
    amount: Decimal = Field(..., gt=0)


class ExploreHoldingOut(BaseModel):
    id: UUID
    scheme_code: str
    scheme_name: str
    category: str
    units: float
    average_nav: float
    invested_amount: float
    current_value: float


class ExploreHoldingWithReturnOut(BaseModel):
    id: UUID
    scheme_code: str
    scheme_name: str
    category: str
    units: float
    average_nav: float
    invested_amount: float
    current_value: float
    return_percentage: float
    nav_is_stale: bool = False
    nav_last_updated: Optional[datetime] = None


class ExploreHoldingsListOut(BaseModel):
    holdings: List[ExploreHoldingWithReturnOut]
    total_invested: float
    total_current_value: float
    overall_return_percentage: float
