import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.modules.settings.models.setting_model import Setting
from app.modules.captcha.models.captcha_model import CaptchaCode


@pytest.mark.asyncio
async def test_generate_captcha(async_client: AsyncClient):
    response = await async_client.get("/api/v1/captcha/generate")
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "svg" in data
    assert data["svg"].startswith("<svg")


@pytest.mark.asyncio
async def test_verify_captcha_valid(db: Session, async_client: AsyncClient):
    gen = await async_client.get("/api/v1/captcha/generate")
    token = gen.json()["token"]

    captcha = db.query(CaptchaCode).filter(CaptchaCode.token == token).first()
    assert captcha is not None

    response = await async_client.post(
        "/api/v1/captcha/verify",
        json={"token": token, "answer": captcha.code},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_verify_captcha_invalid_token(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/captcha/verify",
        json={"token": "nonexistent", "answer": "ABC"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_verify_captcha_invalid_answer(db: Session, async_client: AsyncClient):
    gen = await async_client.get("/api/v1/captcha/generate")
    token = gen.json()["token"]

    response = await async_client.post(
        "/api/v1/captcha/verify",
        json={"token": token, "answer": "WRONG"},
    )
    assert response.status_code == 400

    captcha = db.query(CaptchaCode).filter(CaptchaCode.token == token).first()
    assert captcha.is_used is False


@pytest.mark.asyncio
async def test_verify_captcha_reuse_fails(db: Session, async_client: AsyncClient):
    gen = await async_client.get("/api/v1/captcha/generate")
    token = gen.json()["token"]

    captcha = db.query(CaptchaCode).filter(CaptchaCode.token == token).first()

    response = await async_client.post(
        "/api/v1/captcha/verify",
        json={"token": token, "answer": captcha.code},
    )
    assert response.status_code == 200

    response2 = await async_client.post(
        "/api/v1/captcha/verify",
        json={"token": token, "answer": captcha.code},
    )
    assert response2.status_code == 400


@pytest.mark.asyncio
async def test_auth_login_without_captcha_when_disabled(async_client: AsyncClient):
    payload = {"username": "superadmin", "password": "admin123"}
    response = await async_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_login_requires_captcha_when_enabled(db: Session, async_client: AsyncClient):
    setting = db.query(Setting).filter(Setting.setting_key == "captcha_enabled").first()
    setting.setting_value = "true"
    db.commit()

    payload = {"username": "superadmin", "password": "admin123"}
    response = await async_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 400
    assert "CAPTCHA" in response.json()["message"]


@pytest.mark.asyncio
async def test_auth_login_with_valid_captcha(db: Session, async_client: AsyncClient):
    setting = db.query(Setting).filter(Setting.setting_key == "captcha_enabled").first()
    setting.setting_value = "true"
    db.commit()

    gen = await async_client.get("/api/v1/captcha/generate")
    data = gen.json()
    captcha = db.query(CaptchaCode).filter(CaptchaCode.token == data["token"]).first()

    payload = {
        "username": "superadmin",
        "password": "admin123",
        "captcha_token": data["token"],
        "captcha_answer": captcha.code,
    }
    response = await async_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_requires_captcha_when_enabled(db: Session, async_client: AsyncClient):
    setting = db.query(Setting).filter(Setting.setting_key == "captcha_enabled").first()
    setting.setting_value = "true"
    db.commit()

    payload = {
        "username": "captcha_user",
        "email": "captcha@test.com",
        "full_name": "Captcha User",
        "password": "password123",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "CAPTCHA" in response.json()["message"]


@pytest.mark.asyncio
async def test_register_with_valid_captcha(db: Session, async_client: AsyncClient):
    setting = db.query(Setting).filter(Setting.setting_key == "captcha_enabled").first()
    setting.setting_value = "true"
    db.commit()

    gen = await async_client.get("/api/v1/captcha/generate")
    data = gen.json()
    captcha = db.query(CaptchaCode).filter(CaptchaCode.token == data["token"]).first()

    payload = {
        "username": "captcha_user2",
        "email": "captcha2@test.com",
        "full_name": "Captcha User 2",
        "password": "password123",
        "captcha_token": data["token"],
        "captcha_answer": captcha.code,
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
