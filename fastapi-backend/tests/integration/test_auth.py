import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient):
    payload = {
        "username": "testuser_new",
        "email": "testuser_new@example.com",
        "full_name": "Test User New",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Registration successful. Please login."

@pytest.mark.asyncio
async def test_register_user_duplicate_username(async_client: AsyncClient):
    # Prepare first user (assuming seed or previous test added one)
    payload = {
        "username": "superadmin",
        "email": "unique@example.com",
        "full_name": "Unique User",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["message"] == "Username already taken"

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    payload = {
        "username": "superadmin",
        "password": "admin123"
    }
    response = await async_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "access_token" in data["data"]

@pytest.mark.asyncio
async def test_login_invalid_password(async_client: AsyncClient):
    payload = {
        "username": "superadmin",
        "password": "wrongpassword"
    }
    response = await async_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
