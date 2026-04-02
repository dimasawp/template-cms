import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_users_as_admin(async_client: AsyncClient, admin_token_headers):
    response = await async_client.get("/api/v1/users", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "items" in data["data"]
    assert len(data["data"]["items"]) >= 1

@pytest.mark.asyncio
async def test_create_users_denied_for_normal_user(async_client: AsyncClient, normal_user_token_headers):
    payload = {
        "username": "hacker",
        "email": "hacker@example.com",
        "full_name": "Hacker",
        "password": "securepassword",
    }
    response = await async_client.post("/api/v1/users", json=payload, headers=normal_user_token_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_user_as_admin(async_client: AsyncClient, admin_token_headers):
    payload = {
        "username": "newadmin",
        "email": "newadmin@example.com",
        "full_name": "New Admin",
        "password": "securepassword",
        "role_id": 2, # admin role
        "is_active": True
    }
    response = await async_client.post("/api/v1/users", json=payload, headers=admin_token_headers)
    assert response.status_code == 200 # Defaults to 200
    data = response.json()
    assert data["data"]["username"] == "newadmin"

@pytest.mark.asyncio
async def test_update_user_as_admin(async_client: AsyncClient, admin_token_headers):
    # Get all users first
    res_users = await async_client.get("/api/v1/users", headers=admin_token_headers)
    user_id = res_users.json()["data"]["items"][0]["id"]
    
    payload = {
        "full_name": "Updated Name"
    }
    response = await async_client.put(f"/api/v1/users/{user_id}", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["full_name"] == "Updated Name"
