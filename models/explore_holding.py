from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from db.base import Base


class ExploreHolding(Base):
    __tablename__ = "explore_holdings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False, index=True)
    scheme_code = Column(String(50), nullable=False)
    scheme_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    units = Column(Float, nullable=False, default=0.0)
    average_nav = Column(Float, nullable=False, default=0.0)
    invested_amount = Column(Numeric(14, 2), nullable=False, default=0)
    current_value = Column(Numeric(14, 2), nullable=False, default=0)
    last_known_nav = Column(Float, nullable=True)
    nav_last_updated = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
