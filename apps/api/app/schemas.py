from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserBase(BaseModel):
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class EmployeeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    country: str
    level: str
    status: str
    hire_date: date
    department_name: str
    base_annual: int
    currency: str
    base_usd: float


class EmployeeDetail(EmployeeListItem):
    bonus_annual: int
    monthly_base: float
    total_comp: float
    total_comp_usd: float


class PaginatedEmployees(BaseModel):
    items: list[EmployeeListItem]
    total: int
    page: int
    page_size: int


class CompensationUpdate(BaseModel):
    base_annual: int = Field(..., gt=0)
    bonus_annual: int = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)
    effective_date: date
