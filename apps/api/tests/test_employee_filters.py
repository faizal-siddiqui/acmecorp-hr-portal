import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.employee_repository import EmployeeRepository
from app.models import Employee, Department, Compensation, FxRate
from datetime import date

@pytest.mark.asyncio
async def test_employee_filters_and_sort(db_session: AsyncSession):
    # Setup: Create departments
    dept1 = Department(name="Engineering")
    dept2 = Department(name="Sales")
    db_session.add_all([dept1, dept2])
    await db_session.flush()

    # Setup: Create FX rates
    fx_usd = FxRate(currency="USD", rate_to_usd=1.0, as_of=date(2026, 6, 5))
    fx_eur = FxRate(currency="EUR", rate_to_usd=1.1, as_of=date(2026, 6, 5))
    db_session.add_all([fx_usd, fx_eur])
    await db_session.flush()

    # Setup: Create employees
    e1 = Employee(
        employee_code="E1", first_name="Alice", last_name="Zebra", 
        email="alice@example.com", country="US", level="L3", status="active",
        hire_date=date(2020, 1, 1), department_id=dept1.id
    )
    e2 = Employee(
        employee_code="E2", first_name="Bob", last_name="Alpha", 
        email="bob@example.com", country="DE", level="L1", status="inactive",
        hire_date=date(2021, 1, 1), department_id=dept2.id
    )
    db_session.add_all([e1, e2])
    await db_session.flush()

    # Setup: Create compensations
    c1 = Compensation(
        employee_id=e1.id, base_annual=100000, currency="USD", 
        effective_date=date(2020, 1, 1), is_current=True
    )
    c2 = Compensation(
        employee_id=e2.id, base_annual=80000, currency="EUR", 
        effective_date=date(2021, 1, 1), is_current=True
    )
    db_session.add_all([c1, c2])
    await db_session.commit()

    repo = EmployeeRepository(db_session)

    # Test: Search by name
    items, total = await repo.get_employees(1, 10, q="Alice")
    assert total == 1
    assert items[0].first_name == "Alice"

    # Test: Filter by country
    items, total = await repo.get_employees(1, 10, country="DE")
    assert total == 1
    assert items[0].country == "DE"

    # Test: Filter by status
    items, total = await repo.get_employees(1, 10, status="inactive")
    assert total == 1
    assert items[0].status == "inactive"

    # Test: Sort by name (last_name) asc
    items, total = await repo.get_employees(1, 10, sort_by="name", sort_order="asc")
    assert items[0].last_name == "Alpha" # Bob Alpha
    assert items[1].last_name == "Zebra" # Alice Zebra

    # Test: Sort by name (last_name) desc
    items, total = await repo.get_employees(1, 10, sort_by="name", sort_order="desc")
    assert items[0].last_name == "Zebra"
    assert items[1].last_name == "Alpha"

    # Test: Sort by salary (base_usd)
    # Alice: 100000 * 1.0 = 100000
    # Bob: 80000 * 1.1 = 88000
    items, total = await repo.get_employees(1, 10, sort_by="salary", sort_order="asc")
    assert items[0].first_name == "Bob"
    assert items[1].first_name == "Alice"

    # Test: Combined filters (AND)
    items, total = await repo.get_employees(1, 10, country="US", status="active")
    assert total == 1
    assert items[0].first_name == "Alice"

    items, total = await repo.get_employees(1, 10, country="US", status="inactive")
    assert total == 0
