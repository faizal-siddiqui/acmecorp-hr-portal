from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..services import EmployeeService

router = APIRouter(prefix="/export", tags=["export"], dependencies=[Depends(get_current_user)])


@router.get("/employees.csv")
async def export_employees_csv(
    q: str | None = Query(None),
    country: str | None = Query(None),
    department: str | None = Query(None),
    level: str | None = Query(None),
    status: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    service = EmployeeService(db)
    csv_content = await service.get_employees_csv(
        q, country, department, level, status, sort_by, sort_order
    )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"},
    )
