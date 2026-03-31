from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from schemas.user import UserRegister, UserLogin, TokenOut, UserOut
from core.dependenices import get_current_user
from services.auth_service import get_user_by_id, login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        return await register_user(payload, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        return await login_user(payload, db)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

@router.get("/me", response_model=UserOut)
async def me(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_user_by_id(user_id, db)