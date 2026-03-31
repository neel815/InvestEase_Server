from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependenices import get_current_user
from db.session import get_db
from schemas.concept import ConceptOut
from services.education_service import get_all_concepts

router = APIRouter(prefix="/education", tags=["education"])


@router.get("/concepts", response_model=list[ConceptOut])
async def get_concepts(
    _user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_all_concepts(db)
