from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.session import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardMetricsResponse
from backend.app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/metrics", response_model=DashboardMetricsResponse)
@router.get("/stats", response_model=DashboardMetricsResponse)
async def get_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await DashboardService.get_dashboard_metrics(db, current_user.id)
