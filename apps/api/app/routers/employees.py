from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.employee_service import EmployeeService
from ..schemas import PaginatedEmployees, EmployeeDetail
from ..dependencies import get_current_user

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
