import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.user import User
from backend.app.models.setting import UserSetting
from backend.app.schemas.auth import UserRegister, UserLogin
from backend.app.auth.security import get_password_hash, verify_password
from backend.app.auth.jwt import create_access_token
from backend.app.utils.exceptions import AuthenticationError

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserRegister) -> User:
        clean_email = user_data.email.strip().lower()
        result = await db.execute(select(User).where(User.email == clean_email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise AuthenticationError("Email already registered")

        new_user = User(
            id=str(uuid.uuid4()),
            email=clean_email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name or clean_email.split("@")[0],
            role="user",
            is_active=True
        )
        db.add(new_user)
        await db.flush()

        # Create default user settings
        new_settings = UserSetting(
            id=str(uuid.uuid4()),
            user_id=new_user.id
        )
        db.add(new_settings)

        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, login_data: UserLogin) -> dict:
        clean_email = login_data.email.strip().lower()
        result = await db.execute(select(User).where(User.email == clean_email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        access_token = create_access_token(data={"sub": user.id, "email": user.email})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user": user
        }
