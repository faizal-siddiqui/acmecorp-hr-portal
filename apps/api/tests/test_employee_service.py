from datetime import date, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Compensation, Department, Employee, FxRate, SalaryChangeHistory, User
from app.schemas import CompensationUpdate
from app.services import EmployeeService


@pytest.mark.asyncio
async def test_update_compensation_success(db_session: AsyncSession):
    # Setup
    dept = Department(name="Engineering")
    db_session.add(dept)
    await db_session.flush()

    user = User(email="admin@example.com", password_hash="hash", role="admin")
    db_session.add(user)
    await db_session.flush()

    fx_usd = FxRate(currency="USD", rate_to_usd=1.0, as_of=date(2026, 6, 5))
    db_session.add(fx_usd)
    await db_session.flush()

    emp = Employee(
        employee_code="E1",
        first_name="Alice",
        last_name="Zebra",
        email="alice@example.com",
        country="US",
        level="L3",
        status="active",
        hire_date=date(2020, 1, 1),
        department_id=dept.id,
    )
    db_session.add(emp)
    await db_session.flush()

    comp = Compensation(
        employee_id=emp.id,
        base_annual=100000,
        bonus_annual=10000,
        currency="USD",
        effective_date=date(2020, 1, 1),
        is_current=True,
    )
    db_session.add(comp)
    await db_session.commit()

    service = EmployeeService(db_session)
    update_data = CompensationUpdate(
        base_annual=120000, bonus_annual=15000, currency="USD", effective_date=date(2026, 1, 1)
    )

    # Execute
    updated_comp = await service.update_compensation(emp.id, update_data, user.id)

    # Verify
    assert updated_comp.base_annual == 120000
    assert updated_comp.bonus_annual == 15000
    assert updated_comp.is_current is True

    # Verify old compensation is not current
    stmt = select(Compensation).where(Compensation.id == comp.id)
    result = await db_session.execute(stmt)
    old_comp = result.scalar_one()
    assert old_comp.is_current is False

    # Verify history records
    stmt = select(SalaryChangeHistory).where(SalaryChangeHistory.employee_id == emp.id)
    result = await db_session.execute(stmt)
    history = result.scalars().all()

    # We expect 2 history records: base_annual and bonus_annual
    assert len(history) == 2
    fields = {h.field: h for h in history}

    assert "base_annual" in fields
    assert fields["base_annual"].old_value == "100000"
    assert fields["base_annual"].new_value == "120000"

    assert "bonus_annual" in fields
    assert fields["bonus_annual"].old_value == "10000"
    assert fields["bonus_annual"].new_value == "15000"


@pytest.mark.asyncio
async def test_update_compensation_invalid_currency(db_session: AsyncSession):
    # Setup
    dept = Department(name="Engineering")
    db_session.add(dept)
    await db_session.flush()

    user = User(email="admin@example.com", password_hash="hash", role="admin")
    db_session.add(user)
    await db_session.flush()

    emp = Employee(
        employee_code="E1",
        first_name="Alice",
        last_name="Zebra",
        email="alice@example.com",
        country="US",
        level="L3",
        status="active",
        hire_date=date(2020, 1, 1),
        department_id=dept.id,
    )
    db_session.add(emp)
    await db_session.flush()

    comp = Compensation(
        employee_id=emp.id,
        base_annual=100000,
        bonus_annual=10000,
        currency="USD",
        effective_date=date(2020, 1, 1),
        is_current=True,
    )
    db_session.add(comp)
    await db_session.commit()

    service = EmployeeService(db_session)
    update_data = CompensationUpdate(
        base_annual=120000,
        bonus_annual=15000,
        currency="EUR",  # EUR doesn't exist in FxRate
        effective_date=date(2026, 1, 1),
    )

    # Execute & Verify
    with pytest.raises(ValueError) as excinfo:
        await service.update_compensation(emp.id, update_data, user.id)
    assert "Currency EUR not found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_salary_history(db_session: AsyncSession):
    # Setup
    dept = Department(name="Engineering")
    db_session.add(dept)
    await db_session.flush()

    user = User(email="admin@example.com", password_hash="hash", role="admin")
    db_session.add(user)
    await db_session.flush()

    emp = Employee(
        employee_code="E1",
        first_name="Alice",
        last_name="Zebra",
        email="alice@example.com",
        country="US",
        level="L3",
        status="active",
        hire_date=date(2020, 1, 1),
        department_id=dept.id,
    )
    db_session.add(emp)
    await db_session.flush()

    # Add some history
    h1 = SalaryChangeHistory(
        employee_id=emp.id,
        field="base_annual",
        old_value="100000",
        new_value="110000",
        changed_by=user.id,
        changed_at=datetime(2026, 1, 1),
    )
    h2 = SalaryChangeHistory(
        employee_id=emp.id,
        field="base_annual",
        old_value="110000",
        new_value="120000",
        changed_by=user.id,
        changed_at=datetime(2026, 2, 1),
    )
    db_session.add_all([h1, h2])
    await db_session.commit()

    service = EmployeeService(db_session)
    history = await service.get_employee_salary_history(emp.id)

    assert len(history) == 2
    assert history[0].new_value == "120000"  # Newest first
    assert history[1].new_value == "110000"
    assert history[0].changed_by_email == "admin@example.com"
