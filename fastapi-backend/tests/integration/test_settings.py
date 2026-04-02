import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_public_settings(async_client: AsyncClient):
    response = await async_client.get("/api/v1/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "app_name" in data["data"]

@pytest.mark.asyncio
async def test_bulk_update_settings_as_admin(async_client: AsyncClient):
    # 1. Login as superadmin to get token
    login_payload = {
        "username": "superadmin",
        "password": "admin123"
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200, f"Login failed: {login_res.json()}"
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Update settings
    payload = {
        "settings": [
            {"setting_key": "registration_enabled", "setting_value": "false"}
        ]
    }
    response = await async_client.put("/api/v1/settings/bulk", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.asyncio
async def test_update_settings_denied_for_guest(async_client: AsyncClient):
    payload = {
        "settings": [
            {"setting_key": "registration_enabled", "setting_value": "false"}
        ]
    }
    response = await async_client.put("/api/v1/settings/bulk", json=payload)
    assert response.status_code == 401
