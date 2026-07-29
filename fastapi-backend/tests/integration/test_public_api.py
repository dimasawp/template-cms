import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _create_published_post(async_client: AsyncClient, admin_token_headers):
    """Helper: create a category + published post, return post slug."""
    # Create category
    cat_res = await async_client.post("/api/v1/categories", json={
        "name": "Public Cat", "slug": "public-cat", "is_active": True
    }, headers=admin_token_headers)
    assert cat_res.status_code == 200
    cat_id = cat_res.json()["data"]["id"]

    # Create published post
    post_res = await async_client.post("/api/v1/posts", json={
        "title": "Public Post",
        "slug": "public-post",
        "content": "<p>Public content</p>",
        "category_id": cat_id,
        "status": "PUBLISHED"
    }, headers=admin_token_headers)
    assert post_res.status_code == 200
    return post_res.json()["data"]["slug"]


async def test_get_public_posts(async_client: AsyncClient, admin_token_headers):
    await _create_published_post(async_client, admin_token_headers)

    response = await async_client.get("/api/v1/public/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) >= 1


async def test_get_public_posts_only_shows_published(async_client: AsyncClient, admin_token_headers):
    # Create a draft post (should not appear in public listing)
    cat_res = await async_client.post("/api/v1/categories", json={
        "name": "Draft Cat", "slug": "draft-cat", "is_active": True
    }, headers=admin_token_headers)
    assert cat_res.status_code == 200
    cat_id = cat_res.json()["data"]["id"]

    await async_client.post("/api/v1/posts", json={
        "title": "Draft Post", "slug": "draft-only",
        "content": "test", "category_id": cat_id, "status": "DRAFT"
    }, headers=admin_token_headers)

    response = await async_client.get("/api/v1/public/posts")
    slugs = [item["slug"] for item in response.json()["data"]["items"]]
    assert "draft-only" not in slugs


async def test_get_public_post_detail(async_client: AsyncClient, admin_token_headers):
    slug = await _create_published_post(async_client, admin_token_headers)

    response = await async_client.get(f"/api/v1/public/posts/{slug}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["slug"] == slug
    assert data["data"]["title"] == "Public Post"


async def test_get_public_post_detail_archived(async_client: AsyncClient, admin_token_headers):
    # Create a post then archive it
    cat_res = await async_client.post("/api/v1/categories", json={
        "name": "Archive Cat", "slug": "archive-cat", "is_active": True
    }, headers=admin_token_headers)
    assert cat_res.status_code == 200
    cat_id = cat_res.json()["data"]["id"]

    post_res = await async_client.post("/api/v1/posts", json={
        "title": "Archived Post", "slug": "archived-post",
        "content": "archived", "category_id": cat_id, "status": "PUBLISHED"
    }, headers=admin_token_headers)
    assert post_res.status_code == 200
    post_id = post_res.json()["data"]["id"]

    await async_client.put(f"/api/v1/posts/{post_id}", json={
        "status": "ARCHIVED"
    }, headers=admin_token_headers)

    # Archived post should still be accessible via direct slug
    response = await async_client.get("/api/v1/public/posts/archived-post")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ARCHIVED"


async def test_get_public_post_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/v1/public/posts/nonexistent-slug")
    assert response.status_code == 404


async def test_get_public_categories(async_client: AsyncClient, admin_token_headers):
    await _create_published_post(async_client, admin_token_headers)

    response = await async_client.get("/api/v1/public/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["items"]) >= 1


async def test_get_public_settings(async_client: AsyncClient):
    response = await async_client.get("/api/v1/public/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
