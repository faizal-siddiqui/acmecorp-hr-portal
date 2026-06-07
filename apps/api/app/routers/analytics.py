from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.analytics_service import AnalyticsService
from ..schemas import AnalyticsSummary, AnalyticsBreakdown
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    q: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_summary(q, country, department, level)

@router.get("/breakdown", response_model=AnalyticsBreakdown)
async def get_analytics_breakdown(
    group_by: str = Query(..., pattern="^(country|department|level)$"),
    q: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_breakdown(group_by, q, country, department, level)
