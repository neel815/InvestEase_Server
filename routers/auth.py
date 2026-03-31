from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from jose import JWTError

from db.session import get_db
from schemas.user import UserRegister, UserLogin, TokenOut, UserOut
from core.dependenices import get_current_user
from core.security import decode_token
from core.redis import blacklist_token
from core.dependenices import oauth2_scheme
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

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout user by blacklisting their token"""
    try:
        # Decode token to get expiry info
        payload = decode_token(token)
        exp = payload.get("exp")
        
        if exp is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Calculate remaining seconds until expiry
        current_time = datetime.utcnow().timestamp()
        expiry_seconds = max(1, int(exp - current_time))  # At least 1 second
        
        # Blacklist the token
        await blacklist_token(token, expiry_seconds)
        
        return {"message": "logged out successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")