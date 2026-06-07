from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.employee_repository import EmployeeRepository
from ..schemas import PaginatedEmployees, EmployeeListItem

class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.repository = EmployeeRepository(db)

    async def get_paginated_employees(self, page: int, page_size: int) -> PaginatedEmployees:
        items, total = await self.repository.get_employees(page, page_size)
        
        employee_items = [
            EmployeeListItem(
                id=item.id,
                employee_code=item.employee_code,
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                country=item.country,
                level=item.level,
                status=item.status,
                department_name=item.department_name,
                base_annual=item.base_annual,
                currency=item.currency,
                base_usd=item.base_usd
            )
            for item in items
        ]
        
        return PaginatedEmployees(
            items=employee_items,
            total=total,
            page=page,
            page_size=page_size
        )
