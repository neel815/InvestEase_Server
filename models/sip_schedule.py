from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from db.base import Base


class SIPSchedule(Base):
    __tablename__ = "sip_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False, index=True)
    selected_basket = Column(String, nullable=False)
    monthly_amount = Column(Numeric(12, 2), nullable=False)
    next_due_date = Column(Date, nullable=False)
    sip_day = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
