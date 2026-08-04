from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.session import get_db
from backend.app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from backend.app.services.auth_service import AuthService
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register_user(db, user_data)
    token_resp = await AuthService.authenticate_user(db, UserLogin(email=user.email, password=user_data.password))
    return token_resp

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    token_resp = await AuthService.authenticate_user(db, login_data)
    return token_resp

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    token_resp = await AuthService.authenticate_user(db, login_data)
    return token_resp

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
