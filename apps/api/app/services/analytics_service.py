from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.analytics_repository import AnalyticsRepository
from ..schemas import AnalyticsSummary

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repository = AnalyticsRepository(db)

    async def get_summary(
        self,
        q: Optional[str] = None,
        country: Optional[str] = None,
        department: Optional[str] = None,
        level: Optional[str] = None,
    ) -> AnalyticsSummary:
        data = await self.repository.get_summary_data(q, country, department, level)
        
        # If no data, fx_as_of might be None, but schema requires a date.
        # However, in a real system with seeded FX rates, it shouldn't be None.
        # We'll use a default if it's None for safety, though it shouldn't happen.
        from datetime import date
        return AnalyticsSummary(
            headcount=data["headcount"],
            total_payroll_usd=round(data["total_payroll_usd"], 2),
            avg_payroll_usd=round(data["avg_payroll_usd"], 2),
            median_payroll_usd=round(data["median_payroll_usd"], 2),
            fx_as_of=data["fx_as_of"] or date.today()
        )
