import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.database import get_db
from app.models import User, Employee, Department, Compensation, FxRate
from app.auth import get_password_hash
from datetime import date

@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_analytics_summary_success(client: AsyncClient, db_session: AsyncSession):
    # Setup
    hashed_password = get_password_hash("testpassword")
    user = User(email="hr@example.com", password_hash=hashed_password, role="hr")
    db_session.add(user)
    await db_session.flush()

    dept = Department(name="Engineering")
    db_session.add(dept)
    await db_session.flush()

    # FX Rates: 1 USD = 1 USD, 1 EUR = 1.1 USD
    fx_usd = FxRate(currency="USD", rate_to_usd=1.0, as_of=date(2026, 6, 5))
    fx_eur = FxRate(currency="EUR", rate_to_usd=1.1, as_of=date(2026, 6, 6))
    db_session.add_all([fx_usd, fx_eur])
    await db_session.flush()

    # Employees
    # E1: 100k USD base + 10k bonus = 110k USD
    emp1 = Employee(
        employee_code="E1", first_name="Alice", last_name="A", 
        email="alice@example.com", country="US", level="L3", status="active",
        hire_date=date(2020, 1, 1), department_id=dept.id
    )
    # E2: 80k EUR base + 5k bonus = 85k EUR * 1.1 = 93.5k USD
    emp2 = Employee(
        employee_code="E2", first_name="Bob", last_name="B", 
        email="bob@example.com", country="DE", level="L2", status="active",
        hire_date=date(2021, 1, 1), department_id=dept.id
    )
    # E3: 120k USD base + 20k bonus = 140k USD
    emp3 = Employee(
        employee_code="E3", first_name="Charlie", last_name="C", 
        email="charlie@example.com", country="US", level="L4", status="active",
        hire_date=date(2019, 1, 1), department_id=dept.id
    )
    # E4: Inactive, should be ignored
    emp4 = Employee(
        employee_code="E4", first_name="Dave", last_name="D", 
        email="dave@example.com", country="US", level="L1", status="inactive",
        hire_date=date(2022, 1, 1), department_id=dept.id
    )
    db_session.add_all([emp1, emp2, emp3, emp4])
    await db_session.flush()

    # Compensations
    c1 = Compensation(employee_id=emp1.id, base_annual=100000, bonus_annual=10000, currency="USD", effective_date=date(2020, 1, 1), is_current=True)
    c2 = Compensation(employee_id=emp2.id, base_annual=80000, bonus_annual=5000, currency="EUR", effective_date=date(2021, 1, 1), is_current=True)
    c3 = Compensation(employee_id=emp3.id, base_annual=120000, bonus_annual=20000, currency="USD", effective_date=date(2019, 1, 1), is_current=True)
    c4 = Compensation(employee_id=emp4.id, base_annual=50000, bonus_annual=0, currency="USD", effective_date=date(2022, 1, 1), is_current=True)
    db_session.add_all([c1, c2, c3, c4])
    await db_session.commit()

    # Login
    login_response = await client.post("/auth/login", json={"email": "hr@example.com", "password": "testpassword"})
    token = login_response.json()["access_token"]

    # Execute GET /analytics/summary
    response = await client.get("/analytics/summary", headers={"Authorization": f"Bearer {token}"})

    # Verify
    assert response.status_code == 200
    data = response.json()
    
    # Expected values:
    # Salaries USD: [110000, 93500, 140000]
    # Headcount: 3
    # Total: 110000 + 93500 + 140000 = 343500
    # Avg: 343500 / 3 = 114500
    # Median: sorted [93500, 110000, 140000] -> 110000
    
    assert data["headcount"] == 3
    assert data["total_payroll_usd"] == 343500.0
    assert data["avg_payroll_usd"] == 114500.0
    assert data["median_payroll_usd"] == 110000.0
    assert data["fx_as_of"] == "2026-06-06"

@pytest.mark.asyncio
async def test_get_analytics_summary_with_filters(client: AsyncClient, db_session: AsyncSession):
    # Setup (reusing logic from above but with filters)
    hashed_password = get_password_hash("testpassword")
    user = User(email="hr@example.com", password_hash=hashed_password, role="hr")
    db_session.add(user)
    await db_session.flush()

    dept_eng = Department(name="Engineering")
    dept_hr = Department(name="HR")
    db_session.add_all([dept_eng, dept_hr])
    await db_session.flush()

    fx_usd = FxRate(currency="USD", rate_to_usd=1.0, as_of=date(2026, 6, 5))
    db_session.add(fx_usd)
    await db_session.flush()

    # Alice: Eng, US, L3, 100k
    emp1 = Employee(employee_code="E1", first_name="Alice", last_name="A", email="alice@example.com", country="US", level="L3", status="active", hire_date=date(2020, 1, 1), department_id=dept_eng.id)
    # Bob: HR, DE, L2, 80k
    emp2 = Employee(employee_code="E2", first_name="Bob", last_name="B", email="bob@example.com", country="DE", level="L2", status="active", hire_date=date(2021, 1, 1), department_id=dept_hr.id)
    db_session.add_all([emp1, emp2])
    await db_session.flush()

    c1 = Compensation(employee_id=emp1.id, base_annual=100000, bonus_annual=0, currency="USD", effective_date=date(2020, 1, 1), is_current=True)
    c2 = Compensation(employee_id=emp2.id, base_annual=80000, bonus_annual=0, currency="USD", effective_date=date(2021, 1, 1), is_current=True)
    db_session.add_all([c1, c2])
    await db_session.commit()

    login_response = await client.post("/auth/login", json={"email": "hr@example.com", "password": "testpassword"})
    token = login_response.json()["access_token"]

    # Filter by department=Engineering
    response = await client.get("/analytics/summary?department=Engineering", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["headcount"] == 1
    assert data["total_payroll_usd"] == 100000.0

    # Filter by country=DE
    response = await client.get("/analytics/summary?country=DE", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["headcount"] == 1
    assert data["total_payroll_usd"] == 80000.0
