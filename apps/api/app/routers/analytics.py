from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..schemas import AnalyticsBreakdown, AnalyticsSummary
from ..services import AnalyticsService

router = APIRouter(
    prefix="/analytics", tags=["analytics"], dependencies=[Depends(get_current_user)]
)


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    q: str | None = Query(None),
    country: str | None = Query(None),
    department: str | None = Query(None),
    level: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_summary(q, country, department, level)


@router.get("/breakdown", response_model=AnalyticsBreakdown)
async def get_analytics_breakdown(
    group_by: str = Query(..., pattern="^(country|department|level)$"),
    q: str | None = Query(None),
    country: str | None = Query(None),
    department: str | None = Query(None),
    level: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_breakdown(group_by, q, country, department, level)
