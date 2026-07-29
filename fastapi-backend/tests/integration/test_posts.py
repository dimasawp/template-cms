import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _create_category(async_client, admin_token_headers):
    """Helper: create a category and return its id."""
    payload = {"name": "Test Category", "slug": "test-category", "is_active": True}
    response = await async_client.post("/api/v1/categories", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    return response.json()["data"]["id"]


async def test_create_post(async_client: AsyncClient, admin_token_headers):
    cat_id = await _create_category(async_client, admin_token_headers)

    payload = {
        "title": "Hello World",
        "slug": "hello-world",
        "content": "<p>This is a test post</p>",
        "category_id": cat_id,
        "status": "DRAFT"
    }
    response = await async_client.post("/api/v1/posts", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["title"] == "Hello World"
    assert data["data"]["status"] == "DRAFT"
    return data["data"]["id"]


async def test_get_all_posts(async_client: AsyncClient, admin_token_headers):
    await test_create_post(async_client, admin_token_headers)

    response = await async_client.get("/api/v1/posts", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) >= 1


async def test_get_post_by_id(async_client: AsyncClient, admin_token_headers):
    post_id = await test_create_post(async_client, admin_token_headers)

    response = await async_client.get(f"/api/v1/posts/{post_id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Hello World"


async def test_update_post(async_client: AsyncClient, admin_token_headers):
    post_id = await test_create_post(async_client, admin_token_headers)

    payload = {"title": "Updated Title", "slug": "updated-title"}
    response = await async_client.put(f"/api/v1/posts/{post_id}", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Updated Title"


async def test_delete_post(async_client: AsyncClient, admin_token_headers):
    post_id = await test_create_post(async_client, admin_token_headers)

    response = await async_client.delete(f"/api/v1/posts/{post_id}", headers=admin_token_headers)
    assert response.status_code == 200

    # Verify it's soft-deleted (not found)
    get_response = await async_client.get(f"/api/v1/posts/{post_id}", headers=admin_token_headers)
    assert get_response.status_code == 404


async def test_filter_posts_by_status(async_client: AsyncClient, admin_token_headers):
    cat_id = await _create_category(async_client, admin_token_headers)

    # Create a DRAFT post
    payload = {"title": "Draft Post", "slug": "draft-post", "content": "test", "category_id": cat_id, "status": "DRAFT"}
    await async_client.post("/api/v1/posts", json=payload, headers=admin_token_headers)

    # Create a PUBLISHED post
    payload2 = {"title": "Published Post", "slug": "published-post", "content": "test", "category_id": cat_id, "status": "PUBLISHED"}
    await async_client.post("/api/v1/posts", json=payload2, headers=admin_token_headers)

    # Filter by PUBLISHED
    response = await async_client.get("/api/v1/posts?status=PUBLISHED", headers=admin_token_headers)
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert all(item["status"] == "PUBLISHED" for item in items)


async def test_create_post_denied_without_auth(async_client: AsyncClient):
    payload = {"title": "Hacker Post", "slug": "hacker-post", "content": "test"}
    response = await async_client.post("/api/v1/posts", json=payload)
    assert response.status_code == 401
