from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.employee_repository import EmployeeRepository
from ..schemas import PaginatedEmployees, EmployeeListItem, EmployeeDetail, CompensationUpdate
from ..models import Compensation, SalaryChangeHistory

class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.repository = EmployeeRepository(db)

    async def get_paginated_employees(
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
    ) -> PaginatedEmployees:
        items, total = await self.repository.get_employees(
            page, page_size, q, country, department, level, status, sort_by, sort_order
        )
        
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
                hire_date=item.hire_date,
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

    async def get_employee_detail(self, employee_id: int) -> Optional[EmployeeDetail]:
        item = await self.repository.get_employee_by_id(employee_id)
        if not item:
            return None
        
        monthly_base = item.base_annual / 12
        total_comp = item.base_annual + item.bonus_annual
        total_comp_usd = total_comp * item.rate_to_usd
        
        return EmployeeDetail(
            id=item.id,
            employee_code=item.employee_code,
            first_name=item.first_name,
            last_name=item.last_name,
            email=item.email,
            country=item.country,
            level=item.level,
            status=item.status,
            hire_date=item.hire_date,
            department_name=item.department_name,
            base_annual=item.base_annual,
            bonus_annual=item.bonus_annual,
            currency=item.currency,
            base_usd=item.base_usd,
            monthly_base=monthly_base,
            total_comp=total_comp,
            total_comp_usd=total_comp_usd
        )

    async def update_compensation(
        self, 
        employee_id: int, 
        update_data: CompensationUpdate, 
        changed_by_user_id: int
    ) -> Compensation:
        # Check if currency exists
        fx_rate = await self.repository.get_fx_rate(update_data.currency)
        if not fx_rate:
            raise ValueError(f"Currency {update_data.currency} not found")

        # Get current compensation
        current_comp = await self.repository.get_current_compensation(employee_id)
        if not current_comp:
            raise ValueError(f"No current compensation found for employee {employee_id}")

        history_records = []
        
        # Check for changes and create history records
        if current_comp.base_annual != update_data.base_annual:
            history_records.append(SalaryChangeHistory(
                employee_id=employee_id,
                field="base_annual",
                old_value=str(current_comp.base_annual),
                new_value=str(update_data.base_annual),
                changed_by=changed_by_user_id
            ))
        
        if current_comp.bonus_annual != update_data.bonus_annual:
            history_records.append(SalaryChangeHistory(
                employee_id=employee_id,
                field="bonus_annual",
                old_value=str(current_comp.bonus_annual),
                new_value=str(update_data.bonus_annual),
                changed_by=changed_by_user_id
            ))

        if current_comp.currency != update_data.currency:
            history_records.append(SalaryChangeHistory(
                employee_id=employee_id,
                field="currency",
                old_value=current_comp.currency,
                new_value=update_data.currency,
                changed_by=changed_by_user_id
            ))

        # Create new compensation record
        new_comp = Compensation(
            employee_id=employee_id,
            base_annual=update_data.base_annual,
            bonus_annual=update_data.bonus_annual,
            currency=update_data.currency,
            effective_date=update_data.effective_date,
            is_current=True
        )

        # Perform updates in transaction
        async with self.repository.db.begin_nested():
            await self.repository.deactivate_compensations(employee_id)
            await self.repository.add_compensation(new_comp)
            if history_records:
                await self.repository.add_history_records(history_records)
        
        await self.repository.db.commit()
        return new_comp
