import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_roles_as_admin(async_client: AsyncClient, admin_token_headers):
    response = await async_client.get("/api/v1/roles", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "items" in data["data"]
    assert len(data["data"]["items"]) >= 2  # super_admin + admin

@pytest.mark.asyncio
async def test_get_permissions_as_admin(async_client: AsyncClient, admin_token_headers):
    response = await async_client.get("/api/v1/roles/permissions", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) > 0

@pytest.mark.asyncio
async def test_create_role_as_admin(async_client: AsyncClient, admin_token_headers):
    payload = {
        "name": "moderator",
        "description": "Content Moderator",
        "permission_ids": [1, 5, 9]
    }
    response = await async_client.post("/api/v1/roles", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "moderator"

@pytest.mark.asyncio
async def test_create_role_duplicate(async_client: AsyncClient, admin_token_headers):
    payload = {
        "name": "admin",  # Already exists from seed
        "description": "Duplicate admin",
        "permission_ids": []
    }
    response = await async_client.post("/api/v1/roles", json=payload, headers=admin_token_headers)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_create_role_denied_without_auth(async_client: AsyncClient):
    """Unauthenticated request must be rejected."""
    payload = {
        "name": "hacker_role",
        "description": "Hacker role",
        "permission_ids": []
    }
    response = await async_client.post("/api/v1/roles", json=payload)
    assert response.status_code == 401
