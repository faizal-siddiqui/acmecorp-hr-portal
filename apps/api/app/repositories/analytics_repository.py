import statistics
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Compensation, Department, Employee, FxRate


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary_data(
        self,
        q: str | None = None,
        country: str | None = None,
        department: str | None = None,
        level: str | None = None,
    ) -> dict[str, Any]:
        # Base selection for active employees only
        # We need total_comp_usd for each employee to calculate avg and median
        stmt = (
            select((Compensation.base_annual + Compensation.bonus_annual) * FxRate.rate_to_usd)
            .select_from(Compensation)
            .join(Employee, Employee.id == Compensation.employee_id)
            .join(Department, Employee.department_id == Department.id)
            .join(FxRate, Compensation.currency == FxRate.currency)
            .where(Employee.status == "active")
            .where(Compensation.is_current)
        )

        # Apply filters (same as in EmployeeRepository)
        if q:
            search_filter = or_(
                Employee.first_name.ilike(f"%{q}%"),
                Employee.last_name.ilike(f"%{q}%"),
                Employee.email.ilike(f"%{q}%"),
                Employee.employee_code.ilike(f"%{q}%"),
            )
            stmt = stmt.where(search_filter)

        if country:
            stmt = stmt.where(Employee.country == country)
        if department:
            stmt = stmt.where(Department.name == department)
        if level:
            stmt = stmt.where(Employee.level == level)

        result = await self.db.execute(stmt)
        salaries = [float(row[0]) for row in result.all()]

        if not salaries:
            return {
                "headcount": 0,
                "total_payroll_usd": 0.0,
                "avg_payroll_usd": 0.0,
                "median_payroll_usd": 0.0,
                "fx_as_of": None,
            }

        # Get latest FX as-of date
        fx_stmt = select(func.max(FxRate.as_of))
        fx_result = await self.db.execute(fx_stmt)
        fx_as_of = fx_result.scalar()

        return {
            "headcount": len(salaries),
            "total_payroll_usd": sum(salaries),
            "avg_payroll_usd": sum(salaries) / len(salaries),
            "median_payroll_usd": statistics.median(salaries),
            "fx_as_of": fx_as_of,
        }

    async def get_breakdown_data(
        self,
        group_by: str,
        q: str | None = None,
        country: str | None = None,
        department: str | None = None,
        level: str | None = None,
    ) -> list[dict[str, Any]]:
        # Map group_by string to actual column
        group_col_map = {
            "country": Employee.country,
            "department": Department.name,
            "level": Employee.level,
        }

        if group_by not in group_col_map:
            raise ValueError(f"Invalid group_by: {group_by}")

        group_col = group_col_map[group_by]

        # We need to get all salaries for each group to calculate median
        # For other aggregates, we could use SQL func, but for consistency and median,
        # we'll fetch and group in Python for now.
        # Given 10k records, this is still very fast.

        stmt = (
            select(
                group_col.label("dimension_value"),
                ((Compensation.base_annual + Compensation.bonus_annual) * FxRate.rate_to_usd).label(
                    "total_usd"
                ),
            )
            .select_from(Compensation)
            .join(Employee, Employee.id == Compensation.employee_id)
            .join(Department, Employee.department_id == Department.id)
            .join(FxRate, Compensation.currency == FxRate.currency)
            .where(Employee.status == "active")
            .where(Compensation.is_current)
        )

        # Apply filters
        if q:
            search_filter = or_(
                Employee.first_name.ilike(f"%{q}%"),
                Employee.last_name.ilike(f"%{q}%"),
                Employee.email.ilike(f"%{q}%"),
                Employee.employee_code.ilike(f"%{q}%"),
            )
            stmt = stmt.where(search_filter)

        if country:
            stmt = stmt.where(Employee.country == country)
        if department:
            stmt = stmt.where(Department.name == department)
        if level:
            stmt = stmt.where(Employee.level == level)

        result = await self.db.execute(stmt)
        rows = result.all()

        # Group by dimension_value
        groups: dict[str, list[float]] = {}
        for row in rows:
            val = str(row.dimension_value)
            if val not in groups:
                groups[val] = []
            groups[val].append(float(row.total_usd))

        breakdown = []
        for val, salaries in groups.items():
            breakdown.append(
                {
                    "dimension_value": val,
                    "count": len(salaries),
                    "avg_usd": sum(salaries) / len(salaries),
                    "median_usd": statistics.median(salaries),
                    "min_usd": min(salaries),
                    "max_usd": max(salaries),
                }
            )

        # Sort by dimension value for consistent output
        breakdown.sort(key=lambda x: x["dimension_value"])
        return breakdown
