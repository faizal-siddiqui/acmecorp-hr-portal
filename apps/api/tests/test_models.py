import pytest
from datetime import date, datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models import (
    Department,
    Employee,
    Compensation,
    SalaryChangeHistory,
    FxRate,
    User,
)


@pytest.fixture
async def mem_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def mem_session(mem_engine):
    factory = async_sessionmaker(mem_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


async def test_create_department(mem_session: AsyncSession):
    dept = Department(name="Engineering")
    mem_session.add(dept)
    await mem_session.commit()

    result = await mem_session.execute(select(Department).where(Department.name == "Engineering"))
    saved_dept = result.scalar_one()
    assert saved_dept.id is not None
    assert saved_dept.name == "Engineering"


async def test_create_employee_with_department(mem_session: AsyncSession):
    dept = Department(name="Engineering")
    mem_session.add(dept)
    await mem_session.flush()

    emp = Employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        country="US",
        level="L4",
        status="active",
        hire_date=date(2026, 1, 1),
        department_id=dept.id,
    )
    mem_session.add(emp)
    await mem_session.commit()

    result = await mem_session.execute(select(Employee).where(Employee.employee_code == "EMP001"))
    saved_emp = result.scalar_one()
    assert saved_emp.first_name == "John"
    assert saved_emp.department.name == "Engineering"


async def test_create_compensation(mem_session: AsyncSession):
    dept = Department(name="Engineering")
    mem_session.add(dept)
    await mem_session.flush()

    emp = Employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        country="US",
        level="L4",
        status="active",
        hire_date=date(2026, 1, 1),
        department_id=dept.id,
    )
    mem_session.add(emp)
    await mem_session.flush()

    comp = Compensation(
        employee_id=emp.id,
        base_annual=100000,
        bonus_annual=10000,
        currency="USD",
        effective_date=date(2026, 1, 1),
        is_current=True,
    )
    mem_session.add(comp)
    await mem_session.commit()

    result = await mem_session.execute(select(Compensation).where(Compensation.employee_id == emp.id))
    saved_comp = result.scalar_one()
    assert saved_comp.base_annual == 100000
    assert saved_comp.currency == "USD"


async def test_create_salary_history(mem_session: AsyncSession):
    # Setup user, dept, emp
    user = User(email="hr@example.com", password_hash="hash", role="admin")
    dept = Department(name="Engineering")
    mem_session.add_all([user, dept])
    await mem_session.flush()

    emp = Employee(
        employee_code="EMP001",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        country="US",
        level="L4",
        status="active",
        hire_date=date(2026, 1, 1),
        department_id=dept.id,
    )
    mem_session.add(emp)
    await mem_session.flush()

    history = SalaryChangeHistory(
        employee_id=emp.id,
        field="base_annual",
        old_value="90000",
        new_value="100000",
        changed_by=user.id,
        changed_at=datetime.now(timezone.utc),
        note="Annual increase",
    )
    mem_session.add(history)
    await mem_session.commit()

    result = await mem_session.execute(
        select(SalaryChangeHistory).where(SalaryChangeHistory.employee_id == emp.id)
    )
    saved_history = result.scalar_one()
    assert saved_history.old_value == "90000"
    assert saved_history.changed_by_user.email == "hr@example.com"


async def test_create_fx_rate(mem_session: AsyncSession):
    rate = FxRate(currency="EUR", rate_to_usd=1.1, as_of=date(2026, 1, 1))
    mem_session.add(rate)
    await mem_session.commit()

    result = await mem_session.execute(select(FxRate).where(FxRate.currency == "EUR"))
    saved_rate = result.scalar_one()
    assert saved_rate.rate_to_usd == 1.1


async def test_create_user(mem_session: AsyncSession):
    user = User(email="hr@example.com", password_hash="hash", role="admin")
    mem_session.add(user)
    await mem_session.commit()

    result = await mem_session.execute(select(User).where(User.email == "hr@example.com"))
    saved_user = result.scalar_one()
    assert saved_user.role == "admin"
