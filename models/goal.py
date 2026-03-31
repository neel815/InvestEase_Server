from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from db.base import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    goal_type = Column(String, nullable=False)  # retirement, house, education, wealth
    target_amount = Column(Numeric(14, 2), nullable=False)
    target_date = Column(Date, nullable=False)
    investment_mode = Column(String, nullable=False)  # autopilot, copilot, manual
    selected_basket = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
