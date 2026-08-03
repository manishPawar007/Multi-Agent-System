from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.chats import router as chats_router
from backend.app.api.v1.documents import router as docs_router
from backend.app.api.v1.agents import router as agents_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.settings import router as settings_router
from backend.app.api.v1.users import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(chats_router)
api_router.include_router(docs_router)
api_router.include_router(agents_router)
api_router.include_router(dashboard_router)
api_router.include_router(settings_router)
api_router.include_router(users_router)
