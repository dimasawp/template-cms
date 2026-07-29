from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.helpers.response import success_response, error_response
from app.modules.captcha.schemas.captcha_schema import (
    CaptchaGenerateResponse,
    CaptchaVerifyRequest,
)
from app.modules.captcha.services.captcha_service import create_captcha, verify_captcha

router = APIRouter(prefix="/api/v1/captcha", tags=["Captcha"])


@router.get("/generate", response_model=CaptchaGenerateResponse)
async def generate_captcha(db: Session = Depends(get_db)):
    token, code, svg = create_captcha(db)
    return {"token": token, "svg": svg}


@router.post("/verify")
async def verify_captcha_endpoint(
    payload: CaptchaVerifyRequest,
    db: Session = Depends(get_db),
):
    valid = verify_captcha(db, payload.token, payload.answer)
    if valid:
        return success_response(data={"valid": True}, message="CAPTCHA verified")
    return error_response(message="CAPTCHA verification failed", code=400)
