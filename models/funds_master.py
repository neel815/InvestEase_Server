"""
Master fund directory - stores all available mutual funds with metadata.
Fund details (NAV, history) are fetched individually from MFAPI on demand.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from db.base import Base


class FundsMaster(Base):
    __tablename__ = "funds_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_code = Column(String(20), unique=True, nullable=False, index=True)
    scheme_name = Column(String(255), nullable=False, index=True)
    fund_house = Column(String(100), nullable=True)
    category = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Composite index for common queries
    __table_args__ = (
        Index("ix_funds_master_category_active", "category", "is_active"),
    )

    def __repr__(self):
        return f"<FundsMaster {self.scheme_code}: {self.scheme_name}>"
