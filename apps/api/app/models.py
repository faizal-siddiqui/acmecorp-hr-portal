from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import ForeignKey, Integer, String, Boolean, Date, DateTime, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    employees: Mapped[List["Employee"]] = relationship(back_populates="department")


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(2), index=True, nullable=False)  # ISO 3166-1 alpha-2
    level: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), index=True, nullable=False, default="active")
    department_id: Mapped[int] = mapped_column(
        ForeignKey("department.id"), index=True, nullable=False
    )
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employee.id"), nullable=True)

    department: Mapped["Department"] = relationship(back_populates="employees")
    manager: Mapped[Optional["Employee"]] = relationship(remote_side=[id], backref="subordinates")
    compensations: Mapped[List["Compensation"]] = relationship(back_populates="employee")
    salary_history: Mapped[List["SalaryChangeHistory"]] = relationship(back_populates="employee")


class Compensation(Base):
    __tablename__ = "compensation"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), index=True, nullable=False)
    base_annual: Mapped[int] = mapped_column(Integer, nullable=False)  # Stored as integer
    bonus_annual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO 4217
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=True)

    employee: Mapped["Employee"] = relationship(back_populates="compensations")


class SalaryChangeHistory(Base):
    __tablename__ = "salary_change_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), nullable=False)
    field: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "base_annual"
    old_value: Mapped[str] = mapped_column(Text, nullable=True)
    new_value: Mapped[str] = mapped_column(Text, nullable=False)
    changed_by: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    employee: Mapped["Employee"] = relationship(back_populates="salary_history")
    changed_by_user: Mapped["User"] = relationship()


class FxRate(Base):
    __tablename__ = "fx_rate"

    id: Mapped[int] = mapped_column(primary_key=True)
    currency: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    rate_to_usd: Mapped[float] = mapped_column(Float, nullable=False)
    as_of: Mapped[date] = mapped_column(Date, nullable=False)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
