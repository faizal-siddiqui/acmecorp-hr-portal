from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.employee_service import EmployeeService
from ..schemas import (
    PaginatedEmployees, 
    EmployeeDetail, 
    CompensationUpdate, 
    SalaryHistoryItem,
    EmployeeCreate,
    EmployeeStatusUpdate,
    Department as DepartmentSchema
)
from ..dependencies import get_current_user
from ..models import User

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/", response_model=PaginatedEmployees)
async def get_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    q: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(db)
    return await service.get_paginated_employees(
        page, page_size, q, country, department, level, status, sort_by, sort_order
    )

@router.get("/{employee_id}", response_model=EmployeeDetail)
async def get_employee_detail(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(db)
    employee = await service.get_employee_detail(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.patch("/{employee_id}/compensation")
async def update_compensation(
    employee_id: int,
    update_data: CompensationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = EmployeeService(db)
    try:
        return await service.update_compensation(employee_id, update_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{employee_id}/history", response_model=List[SalaryHistoryItem])
async def get_employee_history(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(db)
    return await service.get_employee_salary_history(employee_id)

@router.post("/", response_model=EmployeeDetail)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(db)
    try:
        employee = await service.create_employee(data)
        # Return detail view
        return await service.get_employee_detail(employee.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{employee_id}/status")
async def update_employee_status(
    employee_id: int,
    data: EmployeeStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(db)
    await service.deactivate_employee(employee_id) if data.status == "inactive" else None
    # For now we only support deactivation via this story, but could expand
    return {"status": data.status}

@router.get("/meta/departments", response_model=List[DepartmentSchema])
async def get_departments(
    db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(db)
    return await service.get_departments()
