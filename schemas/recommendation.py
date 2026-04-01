from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class FundRecommendationOut(BaseModel):
    scheme_code: str
    scheme_name: str
    category: str
    basket_type: str
    returns_1y: Optional[float] = None
    returns_3y: Optional[float] = None
    returns_5y: Optional[float] = None


class RecommendationBasketOut(BaseModel):
    basket_type: str
    recommended: bool
    funds: list[FundRecommendationOut]
    hidden_reason: Optional[str] = None


class GoalRecommendationsOut(BaseModel):
    goal_id: UUID
    recommended_at: datetime
    baskets: list[RecommendationBasketOut]
    horizon: Optional[str] = None
    horizon_note: Optional[str] = None
