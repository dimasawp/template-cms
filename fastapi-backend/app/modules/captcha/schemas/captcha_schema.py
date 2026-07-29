from pydantic import BaseModel


class CaptchaGenerateResponse(BaseModel):
    token: str
    svg: str


class CaptchaVerifyRequest(BaseModel):
    token: str
    answer: str


class CaptchaVerifyResponse(BaseModel):
    valid: bool
