from fastapi import APIRouter, Depends
from backend.app.auth.dependencies import get_current_user
from backend.app.schemas.auth import UserResponse
from backend.app.models.user import User

router = APIRouter(prefix="/users", tags=["Users Profile"])

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
