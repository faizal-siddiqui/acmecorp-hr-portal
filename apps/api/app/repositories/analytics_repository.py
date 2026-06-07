from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from ..models import Employee, Department, Compensation, FxRate
import statistics

class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary_data(
        self,
        q: Optional[str] = None,
        country: Optional[str] = None,
        department: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Base selection for active employees only
        # We need total_comp_usd for each employee to calculate avg and median
        stmt = select(
            (Compensation.base_annual + Compensation.bonus_annual) * FxRate.rate_to_usd
        ).select_from(Compensation) \
         .join(Employee, Employee.id == Compensation.employee_id) \
         .join(Department, Employee.department_id == Department.id) \
         .join(FxRate, Compensation.currency == FxRate.currency) \
         .where(Employee.status == "active") \
         .where(Compensation.is_current == True)

        # Apply filters (same as in EmployeeRepository)
        if q:
            search_filter = or_(
                Employee.first_name.ilike(f"%{q}%"),
                Employee.last_name.ilike(f"%{q}%"),
                Employee.email.ilike(f"%{q}%"),
                Employee.employee_code.ilike(f"%{q}%")
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
                "fx_as_of": None
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
            "fx_as_of": fx_as_of
        }
