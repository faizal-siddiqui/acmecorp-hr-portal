from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc, update
from ..models import Employee, Department, Compensation, FxRate, SalaryChangeHistory

class EmployeeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_employees(
        self,
        page: int,
        page_size: int,
        q: Optional[str] = None,
        country: Optional[str] = None,
        department: Optional[str] = None,
        level: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ):
        offset = (page - 1) * page_size
        
        # Base selection
        stmt = select(
            Employee.id,
            Employee.employee_code,
            Employee.first_name,
            Employee.last_name,
            Employee.email,
            Employee.country,
            Employee.level,
            Employee.status,
            Employee.hire_date,
            Department.name.label("department_name"),
            Compensation.base_annual,
            Compensation.currency,
            (Compensation.base_annual * FxRate.rate_to_usd).label("base_usd")
        ).join(Department, Employee.department_id == Department.id) \
         .join(Compensation, (Employee.id == Compensation.employee_id) & (Compensation.is_current == True)) \
         .join(FxRate, Compensation.currency == FxRate.currency)

        # Filters
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
        if status:
            stmt = stmt.where(Employee.status == status)

        # Sorting
        if sort_by:
            if sort_by == "salary":
                sort_col = (Compensation.base_annual * FxRate.rate_to_usd)
            elif sort_by == "name":
                # For name, we sort by last_name then first_name
                if sort_order == "desc":
                    stmt = stmt.order_by(Employee.last_name.desc(), Employee.first_name.desc())
                else:
                    stmt = stmt.order_by(Employee.last_name.asc(), Employee.first_name.asc())
                sort_col = None # Already handled
            elif sort_by == "hireDate":
                sort_col = Employee.hire_date
            else:
                sort_col = Employee.id
            
            if sort_col is not None:
                if sort_order == "desc":
                    stmt = stmt.order_by(sort_col.desc())
                else:
                    stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(Employee.id)

        # Count query (before limit/offset)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        
        # Apply pagination
        stmt = stmt.offset(offset).limit(page_size)
        
        result = await self.db.execute(stmt)
        items = result.all()
        
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        return items, total

    async def get_employee_by_id(self, employee_id: int):
        stmt = select(
            Employee.id,
            Employee.employee_code,
            Employee.first_name,
            Employee.last_name,
            Employee.email,
            Employee.country,
            Employee.level,
            Employee.status,
            Employee.hire_date,
            Department.name.label("department_name"),
            Compensation.base_annual,
            Compensation.bonus_annual,
            Compensation.currency,
            FxRate.rate_to_usd,
            (Compensation.base_annual * FxRate.rate_to_usd).label("base_usd")
        ).join(Department, Employee.department_id == Department.id) \
         .join(Compensation, (Employee.id == Compensation.employee_id) & (Compensation.is_current == True)) \
         .join(FxRate, Compensation.currency == FxRate.currency) \
         .where(Employee.id == employee_id)
        
        result = await self.db.execute(stmt)
        return result.first()

    async def get_current_compensation(self, employee_id: int) -> Optional[Compensation]:
        stmt = select(Compensation).where(
            (Compensation.employee_id == employee_id) & (Compensation.is_current == True)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_fx_rate(self, currency: str) -> Optional[FxRate]:
        stmt = select(FxRate).where(FxRate.currency == currency)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_compensations(self, employee_id: int):
        stmt = update(Compensation).where(
            (Compensation.employee_id == employee_id) & (Compensation.is_current == True)
        ).values(is_current=False)
        await self.db.execute(stmt)

    async def add_compensation(self, compensation: Compensation):
        self.db.add(compensation)

    async def add_history_records(self, history_records: List[SalaryChangeHistory]):
        self.db.add_all(history_records)
