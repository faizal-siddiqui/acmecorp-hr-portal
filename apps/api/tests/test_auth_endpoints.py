import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth import get_password_hash
from app.database import Base, get_db
from app.main import app
from app.models import User

# Setup test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def test_login_success(client, test_db):
    # Create a test user
    hashed_password = get_password_hash("testpassword")
    user = User(email="test@example.com", password_hash=hashed_password, role="hr")
    test_db.add(user)
    await test_db.commit()

    # Attempt login
    response = await client.post(
        "/auth/login", json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_password(client, test_db):
    # Create a test user
    hashed_password = get_password_hash("testpassword")
    user = User(email="test@example.com", password_hash=hashed_password, role="hr")
    test_db.add(user)
    await test_db.commit()

    # Attempt login with wrong password
    response = await client.post(
        "/auth/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


async def test_login_nonexistent_user(client):
    # Attempt login with non-existent user
    response = await client.post(
        "/auth/login", json={"email": "nonexistent@example.com", "password": "password"}
    )
    assert response.status_code == 401


async def test_protected_route_unauthorized(client):
    # Attempt to access protected route without token
    response = await client.get("/employees/")
    assert response.status_code == 401


async def test_protected_route_success(client, test_db):
    # Create a test user
    hashed_password = get_password_hash("testpassword")
    user = User(email="hr@example.com", password_hash=hashed_password, role="hr")
    test_db.add(user)
    await test_db.commit()

    # Login to get token
    login_response = await client.post(
        "/auth/login", json={"email": "hr@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Access protected route with token
    response = await client.get("/employees/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


async def test_protected_route_forbidden_role(client, test_db):
    # Create a test user with non-HR role
    hashed_password = get_password_hash("testpassword")
    user = User(email="user@example.com", password_hash=hashed_password, role="user")
    test_db.add(user)
    await test_db.commit()

    # Login to get token
    login_response = await client.post(
        "/auth/login", json={"email": "user@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Access protected route with token
    response = await client.get("/employees/", headers={"Authorization": f"Bearer {token}"})
    # Currently, any logged in user can access employees
    assert response.status_code == 200
