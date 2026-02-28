"""API dependencies."""
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings
from app.services.auth import decode_token
from app.models.user import UserInDB

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserInDB:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = decode_token(credentials.credentials)
    if not token_data or not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    if token_data.username != settings.ALLOWED_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserInDB(
        id=0,
        username=token_data.username,
        hashed_password="",
        created_at=datetime.utcnow(),
    )
