import pytest
from httpx import AsyncClient

# Injecting one notification dynamically would be best, but we'll try to read empty state first
# Or we can just create one by accessing the DB if necessary. For now let's just test endpoints.

@pytest.mark.asyncio
async def test_get_notifications(async_client: AsyncClient, normal_user_token_headers):
    response = await async_client.get("/api/v1/notifications", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "items" in data["data"]
    assert type(data["data"]["items"]) == list

@pytest.mark.asyncio
async def test_get_notification_badge(async_client: AsyncClient, normal_user_token_headers):
    response = await async_client.get("/api/v1/notifications/badge", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "unread_count" in data["data"]
    assert type(data["data"]["unread_count"]) == int

@pytest.mark.asyncio
async def test_mark_all_read(async_client: AsyncClient, normal_user_token_headers):
    response = await async_client.put("/api/v1/notifications/read-all", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "marked" in data["data"]
