"""Authentication service."""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import UserModel
from app.models.user import User, UserCreate, UserInDB, TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> tuple[str, int]:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def decode_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


async def get_user_by_username(db: AsyncSession, username: str) -> UserInDB | None:
    result = await db.execute(select(UserModel).where(UserModel.username == username))
    user = result.scalar_one_or_none()
    if user:
        return UserInDB(
            id=user.id,
            username=user.username,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
    return None


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    hashed = get_password_hash(user_create.password)
    user = UserModel(username=user_create.username, hashed_password=hashed)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return User(id=user.id, username=user.username, created_at=user.created_at)
