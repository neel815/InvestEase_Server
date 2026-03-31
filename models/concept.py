from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(80), nullable=True)
    read_time_minutes = Column(Integer, nullable=True)
    order_index = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    number_example = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
