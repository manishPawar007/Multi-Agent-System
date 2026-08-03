import sys
import uuid
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from backend.app.config.settings import settings
from backend.app.database.base import Base
from backend.app.models.user import User
from backend.app.models.setting import UserSetting
from backend.app.auth.security import get_password_hash
from backend.app.utils.logger import logger

db_url = settings.DATABASE_URL

try:
    engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
    )
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise e

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default accounts on fresh deployment
    async with AsyncSessionLocal() as session:
        try:
            # Seed Account 1: manish@gmail.com
            res1 = await session.execute(select(User).where(User.email == "manish@gmail.com"))
            if not res1.scalar_one_or_none():
                u1_id = str(uuid.uuid4())
                u1 = User(
                    id=u1_id,
                    email="manish@gmail.com",
                    hashed_password=get_password_hash("password123"),
                    full_name="Manish Pawar",
                    role="admin",
                    is_active=True
                )
                session.add(u1)
                session.add(UserSetting(id=str(uuid.uuid4()), user_id=u1_id))

            # Seed Account 2: admin@omniagent.ai
            res2 = await session.execute(select(User).where(User.email == "admin@omniagent.ai"))
            if not res2.scalar_one_or_none():
                u2_id = str(uuid.uuid4())
                u2 = User(
                    id=u2_id,
                    email="admin@omniagent.ai",
                    hashed_password=get_password_hash("admin123"),
                    full_name="OmniAgent Admin",
                    role="admin",
                    is_active=True
                )
                session.add(u2)
                session.add(UserSetting(id=str(uuid.uuid4()), user_id=u2_id))

            await session.commit()
        except Exception as ex:
            logger.warning(f"Default user seeding notice: {ex}")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
