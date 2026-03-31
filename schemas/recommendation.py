from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FundRecommendationOut(BaseModel):
    scheme_code: str
    scheme_name: str
    category: str
    basket_type: str
    returns_1y: float
    returns_3y: float
    returns_5y: float


class RecommendationBasketOut(BaseModel):
    basket_type: str
    recommended: bool
    funds: list[FundRecommendationOut]


class GoalRecommendationsOut(BaseModel):
    goal_id: UUID
    recommended_at: datetime
    baskets: list[RecommendationBasketOut]
