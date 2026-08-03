import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database.session import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.setting import UserSetting
from backend.app.schemas.setting import UserSettingResponse, UserSettingUpdate

router = APIRouter(prefix="/settings", tags=["User Settings"])

@router.get("", response_model=UserSettingResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(UserSetting).where(UserSetting.user_id == current_user.id))
    sett = res.scalar_one_or_none()
    if not sett:
        sett = UserSetting(id=str(uuid.uuid4()), user_id=current_user.id)
        db.add(sett)
        await db.commit()
        await db.refresh(sett)
    return sett

@router.put("", response_model=UserSettingResponse)
async def update_settings(
    update_data: UserSettingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(UserSetting).where(UserSetting.user_id == current_user.id))
    sett = res.scalar_one_or_none()
    if not sett:
        sett = UserSetting(id=str(uuid.uuid4()), user_id=current_user.id)
        db.add(sett)

    update_dict = update_data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        if v is not None:
            setattr(sett, k, v)

    await db.commit()
    await db.refresh(sett)
    return sett
