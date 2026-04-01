from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from db.base import Base


class PortfolioSummary(Base):
    __tablename__ = "portfolio_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False, index=True)
    total_invested = Column(Numeric(14, 2), nullable=False, default=0)
    current_value = Column(Numeric(14, 2), nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
