from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models import Compensation, Department, Employee, FxRate, SalaryChangeHistory


class EmployeeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_employees(
        self,
        page: int | None,
        page_size: int | None,
        q: str | None = None,
        country: str | None = None,
        department: str | None = None,
        level: str | None = None,
        status: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ):
        # Base selection
        stmt = (
            select(
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
                (Compensation.base_annual * FxRate.rate_to_usd).label("base_usd"),
            )
            .join(Department, Employee.department_id == Department.id)
            .join(
                Compensation,
                (Employee.id == Compensation.employee_id) & (Compensation.is_current),
            )
            .join(FxRate, Compensation.currency == FxRate.currency)
        )

        # Filters
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
        if status:
            stmt = stmt.where(Employee.status == status)

        # Sorting
        if sort_by:
            if sort_by == "salary":
                sort_col = Compensation.base_annual * FxRate.rate_to_usd
            elif sort_by == "name":
                # For name, we sort by last_name then first_name
                if sort_order == "desc":
                    stmt = stmt.order_by(Employee.last_name.desc(), Employee.first_name.desc())
                else:
                    stmt = stmt.order_by(Employee.last_name.asc(), Employee.first_name.asc())
                sort_col = None  # Already handled
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

        # Apply pagination if provided
        if page is not None and page_size is not None:
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size)

        result = await self.db.execute(stmt)
        items = result.all()

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        return items, total

    async def get_employee_by_id(self, employee_id: int):
        stmt = (
            select(
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
                (Compensation.base_annual * FxRate.rate_to_usd).label("base_usd"),
            )
            .join(Department, Employee.department_id == Department.id)
            .join(
                Compensation,
                (Employee.id == Compensation.employee_id) & (Compensation.is_current),
            )
            .join(FxRate, Compensation.currency == FxRate.currency)
            .where(Employee.id == employee_id)
        )

        result = await self.db.execute(stmt)
        return result.first()

    async def get_current_compensation(self, employee_id: int) -> Compensation | None:
        stmt = select(Compensation).where(
            (Compensation.employee_id == employee_id) & (Compensation.is_current)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_fx_rate(self, currency: str) -> FxRate | None:
        stmt = select(FxRate).where(FxRate.currency == currency)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_compensations(self, employee_id: int):
        stmt = (
            update(Compensation)
            .where((Compensation.employee_id == employee_id) & (Compensation.is_current))
            .values(is_current=False)
        )
        await self.db.execute(stmt)

    async def add_compensation(self, compensation: Compensation):
        self.db.add(compensation)

    async def add_history_records(self, history_records: list[SalaryChangeHistory]):
        self.db.add_all(history_records)

    async def get_salary_history(self, employee_id: int) -> list[SalaryChangeHistory]:
        stmt = (
            select(SalaryChangeHistory)
            .where(SalaryChangeHistory.employee_id == employee_id)
            .options(joinedload(SalaryChangeHistory.changed_by_user))
            .order_by(SalaryChangeHistory.changed_at.desc())
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_employee(self, employee: Employee) -> Employee:
        self.db.add(employee)
        return employee

    async def update_employee_status(self, employee_id: int, status: str):
        stmt = update(Employee).where(Employee.id == employee_id).values(status=status)
        await self.db.execute(stmt)

    async def get_departments(self) -> list[Department]:
        stmt = select(Department).order_by(Department.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()
