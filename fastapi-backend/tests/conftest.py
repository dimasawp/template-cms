import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_mock_engine, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from main import app
from app.core.database import Base, get_db
from app.seeds.seed import seed_roles, seed_permissions, seed_role_permissions, seed_users, seed_settings

# Use SQLite in-memory for fast testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_roles(db)
        seed_permissions(db)
        db.flush()
        seed_role_permissions(db)
        seed_users(db)
        seed_settings(db)
        db.commit()
    finally:
        db.close()
    
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(db) -> AsyncGenerator:
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
async def admin_token_headers(async_client: AsyncClient):
    login_payload = {
        "username": "superadmin",
        "password": "admin123"
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200, "Failed to authenticate as super_admin in test fixture"
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def normal_user_token_headers(async_client: AsyncClient):
    # Register a new normal user first
    payload = {
        "username": "normaluser",
        "email": "normaluser@example.com",
        "full_name": "Normal User",
        "password": "password123"
    }
    await async_client.post("/api/v1/auth/register", json=payload)
    
    # Login
    login_payload = {
        "username": "normaluser",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200, "Failed to authenticate normal user in test fixture"
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
