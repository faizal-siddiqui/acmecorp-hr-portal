from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import AnalyticsRepository
from ..schemas import AnalyticsBreakdown, AnalyticsBreakdownItem, AnalyticsSummary


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repository = AnalyticsRepository(db)

    async def get_summary(
        self,
        q: str | None = None,
        country: str | None = None,
        department: str | None = None,
        level: str | None = None,
    ) -> AnalyticsSummary:
        data = await self.repository.get_summary_data(q, country, department, level)

        return AnalyticsSummary(
            headcount=data["headcount"],
            total_payroll_usd=round(data["total_payroll_usd"], 2),
            avg_payroll_usd=round(data["avg_payroll_usd"], 2),
            median_payroll_usd=round(data["median_payroll_usd"], 2),
            fx_as_of=data["fx_as_of"] or date.today(),
        )

    async def get_breakdown(
        self,
        group_by: str,
        q: str | None = None,
        country: str | None = None,
        department: str | None = None,
        level: str | None = None,
    ) -> AnalyticsBreakdown:
        data = await self.repository.get_breakdown_data(group_by, q, country, department, level)

        items = [
            AnalyticsBreakdownItem(
                dimension_value=item["dimension_value"],
                count=item["count"],
                avg_usd=round(item["avg_usd"], 2),
                median_usd=round(item["median_usd"], 2),
                min_usd=round(item["min_usd"], 2),
                max_usd=round(item["max_usd"], 2),
            )
            for item in data
        ]

        return AnalyticsBreakdown(group_by=group_by, items=items)
