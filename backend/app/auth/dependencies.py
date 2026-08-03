import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.setting import UserSetting
from backend.app.auth.jwt import decode_access_token
from backend.app.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login", auto_error=False)

DEFAULT_LOCAL_USER_ID = "default-local-user-id"

async def get_or_create_default_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == DEFAULT_LOCAL_USER_ID))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=DEFAULT_LOCAL_USER_ID,
            email="local@omniagent.ai",
            hashed_password="guest_local_user",
            full_name="Local User",
            role="admin",
            is_active=True
        )
        db.add(user)

        user_setting = UserSetting(
            id=str(uuid.uuid4()),
            user_id=DEFAULT_LOCAL_USER_ID
        )
        db.add(user_setting)
        await db.commit()
        await db.refresh(user)

    return user

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user
