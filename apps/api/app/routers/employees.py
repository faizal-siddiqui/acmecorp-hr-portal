from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_hr_user
from .. import models

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/")
async def get_employees(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_hr_user),
):
    return {"message": f"Hello {current_user.email}, here are the employees."}
