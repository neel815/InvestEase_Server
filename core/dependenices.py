from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from core.security import decode_token
from core.redis import is_token_blacklisted
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if token is blacklisted
        if await is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token has been invalidated")
            
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id