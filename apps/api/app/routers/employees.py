from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.employee_service import EmployeeService
from ..schemas import PaginatedEmployees
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
    db: AsyncSession = Depends(get_db)
):
    service = EmployeeService(db)
    return await service.get_paginated_employees(page, page_size)
