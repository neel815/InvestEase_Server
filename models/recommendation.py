from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False, index=True)
    scheme_code = Column(String(40), nullable=False)
    scheme_name = Column(String(160), nullable=False)
    category = Column(String(80), nullable=False)
    basket_type = Column(String(20), nullable=False)
    returns_1y = Column(Float, nullable=False)
    returns_3y = Column(Float, nullable=False)
    returns_5y = Column(Float, nullable=False)
    recommended_at = Column(DateTime, default=datetime.utcnow, nullable=False)
