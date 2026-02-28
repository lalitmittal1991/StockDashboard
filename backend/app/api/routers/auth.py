"""Authentication routes - single allowed user, no registration."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.models.user import User, Token
from app.services.auth import create_access_token
from app.api.deps import get_current_user
from app.models.user import UserInDB

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username and password. Only the configured allowed user can login."""
    settings = get_settings()
    if not settings.ALLOWED_USERNAME or not settings.ALLOWED_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth not configured. Set ALLOWED_USERNAME and ALLOWED_PASSWORD.",
        )
    if form_data.username != settings.ALLOWED_USERNAME or form_data.password != settings.ALLOWED_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token, expires_in = create_access_token(data={"sub": settings.ALLOWED_USERNAME})
    return Token(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=User)
async def me(current_user: UserInDB = Depends(get_current_user)):
    """Get current user info."""
    return User(id=0, username=current_user.username, created_at=current_user.created_at)
