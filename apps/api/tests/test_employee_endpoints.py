import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.main import app
from app.database import get_db
from app.models import User, Employee, Department, Compensation, FxRate, SalaryChangeHistory
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
async def test_patch_compensation_success(client: AsyncClient, db_session: AsyncSession):
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

    emp = Employee(
        employee_code="E1", first_name="Alice", last_name="Zebra", 
        email="alice@example.com", country="US", level="L3", status="active",
        hire_date=date(2020, 1, 1), department_id=dept.id
    )
    db_session.add(emp)
    await db_session.flush()

    comp = Compensation(
        employee_id=emp.id, base_annual=100000, bonus_annual=10000, currency="USD", 
        effective_date=date(2020, 1, 1), is_current=True
    )
    db_session.add(comp)
    await db_session.commit()

    # Login to get token
    login_response = await client.post(
        "/auth/login",
        json={"email": "hr@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Execute PATCH
    update_data = {
        "base_annual": 120000,
        "bonus_annual": 15000,
        "currency": "USD",
        "effective_date": "2026-01-01"
    }
    response = await client.patch(
        f"/employees/{emp.id}/compensation",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["base_annual"] == 120000
    assert data["bonus_annual"] == 15000
    assert data["is_current"] is True

@pytest.mark.asyncio
async def test_patch_compensation_invalid_data(client: AsyncClient, db_session: AsyncSession):
    # Setup
    hashed_password = get_password_hash("testpassword")
    user = User(email="hr@example.com", password_hash=hashed_password, role="hr")
    db_session.add(user)
    await db_session.flush()

    emp = Employee(
        employee_code="E1", first_name="Alice", last_name="Zebra", 
        email="alice@example.com", country="US", level="L3", status="active",
        hire_date=date(2020, 1, 1), department_id=1 # Assuming dept 1 exists or not needed for this test
    )
    # ... actually need full setup to avoid FK issues if enforced
    
    await db_session.commit()

    # Login to get token
    login_response = await client.post(
        "/auth/login",
        json={"email": "hr@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Execute PATCH with invalid data (base_annual <= 0)
    update_data = {
        "base_annual": 0,
        "bonus_annual": 15000,
        "currency": "USD",
        "effective_date": "2026-01-01"
    }
    response = await client.patch(
        "/employees/1/compensation",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Verify
    assert response.status_code == 422 # Pydantic validation error

@pytest.mark.asyncio
async def test_get_history_endpoint(client: AsyncClient, db_session: AsyncSession):
    # Setup
    hashed_password = get_password_hash("testpassword")
    user = User(email="hr@example.com", password_hash=hashed_password, role="hr")
    db_session.add(user)
    await db_session.flush()

    emp = Employee(
        employee_code="E1", first_name="Alice", last_name="Zebra", 
        email="alice@example.com", country="US", level="L3", status="active",
        hire_date=date(2020, 1, 1), department_id=1
    )
    db_session.add(emp)
    await db_session.flush()

    h1 = SalaryChangeHistory(
        employee_id=emp.id, field="base_annual", old_value="100000", new_value="110000",
        changed_by=user.id
    )
    db_session.add(h1)
    await db_session.commit()

    # Login to get token
    login_response = await client.post(
        "/auth/login",
        json={"email": "hr@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Execute GET history
    response = await client.get(
        f"/employees/{emp.id}/history",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["field"] == "base_annual"
    assert data[0]["changed_by_email"] == "hr@example.com"

@pytest.mark.asyncio
async def test_create_employee_success(client: AsyncClient, db_session: AsyncSession):
    # Setup
    dept = Department(name="Engineering")
    db_session.add(dept)
    fx_usd = FxRate(currency="USD", rate_to_usd=1.0, as_of=date(2026, 6, 5))
    db_session.add(fx_usd)
    
    hashed_password = get_password_hash("testpassword")
    user = User(email="hr@example.com", password_hash=hashed_password, role="hr")
    db_session.add(user)
    await db_session.commit()

    # Login
    login_response = await client.post(
        "/auth/login",
        json={"email": "hr@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Create employee
    new_employee_data = {
        "employee_code": "NEW001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "country": "US",
        "level": "L1",
        "hire_date": "2026-06-01",
        "department_id": dept.id,
        "base_annual": 80000,
        "bonus_annual": 5000,
        "currency": "USD"
    }
    
    response = await client.post(
        "/employees/",
        json=new_employee_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["employee_code"] == "NEW001"
    assert data["first_name"] == "John"
    assert data["base_annual"] == 80000
    assert data["status"] == "active"

@pytest.mark.asyncio
async def test_deactivate_employee(client: AsyncClient, db_session: AsyncSession):
    # Setup
    dept = Department(name="Engineering")
    db_session.add(dept)
    fx_usd = FxRate(currency="USD", rate_to_usd=1.0, as_of=date(2026, 6, 5))
    db_session.add(fx_usd)
    
    hashed_password = get_password_hash("testpassword")
    user = User(email="hr@example.com", password_hash=hashed_password, role="hr")
    db_session.add(user)
    await db_session.flush()

    emp = Employee(
        employee_code="E1", first_name="Alice", last_name="Zebra", 
        email="alice@example.com", country="US", level="L3", status="active",
        hire_date=date(2020, 1, 1), department_id=dept.id
    )
    db_session.add(emp)
    await db_session.commit()

    # Login
    login_response = await client.post(
        "/auth/login",
        json={"email": "hr@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Deactivate
    response = await client.patch(
        f"/employees/{emp.id}/status",
        json={"status": "inactive"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

    # Verify in DB
    stmt = select(Employee).where(Employee.id == emp.id)
    result = await db_session.execute(stmt)
    updated_emp = result.scalar_one()
    assert updated_emp.status == "inactive"
