from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ConceptOut(BaseModel):
    id: UUID
    title: str
    summary: str
    explanation: str
    number_example: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
