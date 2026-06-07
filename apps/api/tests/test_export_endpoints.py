import pytest
import csv
import io
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
async def test_export_employees_csv_success(client: AsyncClient, db_session: AsyncSession):
    # Setup
    hashed_password = get_password_hash("testpassword")
    user = User(email="hr@example.com", password_hash=hashed_password, role="hr")
    db_session.add(user)
    await db_session.flush()

    dept = Department(name="Engineering")
    db_session.add(dept)
    await db_session.flush()

    fx_usd = FxRate(currency="USD", rate_to_usd=1.0, as_of=date(2026, 6, 5))
    db_session.add(fx_usd)
    await db_session.flush()

    emp1 = Employee(
        employee_code="E1", first_name="Alice", last_name="A", 
        email="alice@example.com", country="US", level="L3", status="active",
        hire_date=date(2020, 1, 1), department_id=dept.id
    )
    db_session.add(emp1)
    await db_session.flush()

    c1 = Compensation(employee_id=emp1.id, base_annual=100000, bonus_annual=10000, currency="USD", effective_date=date(2020, 1, 1), is_current=True)
    db_session.add(c1)
    await db_session.commit()

    # Login
    login_response = await client.post("/auth/login", json={"email": "hr@example.com", "password": "testpassword"})
    token = login_response.json()["access_token"]

    # Execute GET /export/employees.csv
    response = await client.get("/export/employees.csv", headers={"Authorization": f"Bearer {token}"})

    # Verify
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=employees.csv" in response.headers["content-disposition"]
    
    csv_content = response.text
    f = io.StringIO(csv_content)
    reader = csv.DictReader(f)
    rows = list(reader)
    
    assert len(rows) == 1
    assert rows[0]["Employee Code"] == "E1"
    assert rows[0]["First Name"] == "Alice"
    assert rows[0]["Last Name"] == "A"
    assert rows[0]["Email"] == "alice@example.com"
    assert rows[0]["Country"] == "US"
    assert rows[0]["Department"] == "Engineering"
    assert rows[0]["Level"] == "L3"
    assert rows[0]["Status"] == "active"
    assert rows[0]["Base Annual"] == "100000"
    assert rows[0]["Currency"] == "USD"

@pytest.mark.asyncio
async def test_export_employees_csv_with_filters(client: AsyncClient, db_session: AsyncSession):
    # Setup
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

    emp1 = Employee(employee_code="E1", first_name="Alice", last_name="A", email="alice@example.com", country="US", level="L3", status="active", hire_date=date(2020, 1, 1), department_id=dept_eng.id)
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
    response = await client.get("/export/employees.csv?department=Engineering", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    csv_content = response.text
    f = io.StringIO(csv_content)
    reader = csv.DictReader(f)
    rows = list(reader)
    
    assert len(rows) == 1
    assert rows[0]["Employee Code"] == "E1"
    assert rows[0]["Department"] == "Engineering"

    # Filter by country=DE
    response = await client.get("/export/employees.csv?country=DE", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    f = io.StringIO(response.text)
    reader = csv.DictReader(f)
    rows = list(reader)
    
    assert len(rows) == 1
    assert rows[0]["Employee Code"] == "E2"
    assert rows[0]["Country"] == "DE"
