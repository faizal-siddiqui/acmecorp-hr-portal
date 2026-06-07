from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models import Employee, Department, Compensation, FxRate

class EmployeeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_employees(self, page: int, page_size: int):
        offset = (page - 1) * page_size
        
        # Base query for items
        query = (
            select(
                Employee.id,
                Employee.employee_code,
                Employee.first_name,
                Employee.last_name,
                Employee.email,
                Employee.country,
                Employee.level,
                Employee.status,
                Department.name.label("department_name"),
                Compensation.base_annual,
                Compensation.currency,
                (Compensation.base_annual * FxRate.rate_to_usd).label("base_usd")
            )
            .join(Department, Employee.department_id == Department.id)
            .join(Compensation, (Employee.id == Compensation.employee_id) & (Compensation.is_current == True))
            .join(FxRate, Compensation.currency == FxRate.currency)
            .order_by(Employee.id)
            .offset(offset)
            .limit(page_size)
        )
        
        result = await self.db.execute(query)
        items = result.all()
        
        # Query for total count
        count_query = select(func.count(Employee.id))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        return items, total
