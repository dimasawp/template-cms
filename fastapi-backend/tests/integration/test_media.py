import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_upload_media(async_client: AsyncClient, admin_token_headers):
    # httpx accepts files as a dict
    files = {"file": ("test_file.png", b"test content", "image/png")}
    response = await async_client.post("/api/v1/media/upload", files=files, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "filename" in data["data"]
    assert data["data"]["original_name"] == "test_file.png"
