"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.db.database import get_db
from app.models.user import UserCreate, User, Token
from app.services.auth import (
    get_user_by_username,
    verify_password,
    create_user,
    create_access_token,
)
from app.api.deps import get_current_user
from app.models.user import UserInDB

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    existing = await get_user_by_username(db, user_create.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return await create_user(db, user_create)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login with username and password."""
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token, expires_in = create_access_token(data={"sub": user.username})
    return Token(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=User)
async def me(current_user: UserInDB = Depends(get_current_user)):
    """Get current user info."""
    return User(id=current_user.id, username=current_user.username, created_at=current_user.created_at)
