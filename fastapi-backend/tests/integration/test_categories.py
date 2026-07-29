import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_category(async_client: AsyncClient, admin_token_headers):
    payload = {
        "name": "Berita",
        "slug": "berita",
        "description": "Category for news",
        "is_active": True
    }
    response = await async_client.post("/api/v1/categories", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == "Berita"
    assert data["data"]["slug"] == "berita"
    return data["data"]["id"]


async def test_get_all_categories(async_client: AsyncClient, admin_token_headers):
    # First create one
    await test_create_category(async_client, admin_token_headers)

    response = await async_client.get("/api/v1/categories", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) >= 1


async def test_get_category_by_id(async_client: AsyncClient, admin_token_headers):
    cat_id = await test_create_category(async_client, admin_token_headers)

    response = await async_client.get(f"/api/v1/categories/{cat_id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Berita"


async def test_create_subcategory(async_client: AsyncClient, admin_token_headers):
    parent_id = await test_create_category(async_client, admin_token_headers)

    payload = {
        "name": "Olahraga",
        "slug": "olahraga",
        "parent_id": parent_id,
        "is_active": True
    }
    response = await async_client.post("/api/v1/categories", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["parent_id"] == parent_id


async def test_update_category(async_client: AsyncClient, admin_token_headers):
    cat_id = await test_create_category(async_client, admin_token_headers)

    payload = {"name": "Berita Terbaru", "slug": "berita-terbaru"}
    response = await async_client.put(f"/api/v1/categories/{cat_id}", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Berita Terbaru"


async def test_delete_category(async_client: AsyncClient, admin_token_headers):
    cat_id = await test_create_category(async_client, admin_token_headers)

    response = await async_client.delete(f"/api/v1/categories/{cat_id}", headers=admin_token_headers)
    assert response.status_code == 200

    # Verify it's deleted
    get_response = await async_client.get(f"/api/v1/categories/{cat_id}", headers=admin_token_headers)
    assert get_response.status_code == 404


async def test_create_category_denied_without_auth(async_client: AsyncClient):
    payload = {"name": "Hacker", "slug": "hacker"}
    response = await async_client.post("/api/v1/categories", json=payload)
    assert response.status_code == 401
