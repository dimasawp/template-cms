import os
import random
import string
import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.captcha.models.captcha_model import CaptchaCode

_CHARS = string.digits + string.ascii_uppercase
# Ambiguous chars removed: 0, O, I, 1
_SAFE_CHARS = [c for c in _CHARS if c not in ("0", "O", "I", "1")]


def generate_code(length: int = 5) -> str:
    return "".join(random.choices(_SAFE_CHARS, k=length))


def generate_svg(code: str) -> str:
    width = 28 * len(code) + 20
    height = 50
    char_width = 24

    elements = []

    # Background
    elements.append(
        f'<rect width="{width}" height="{height}" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>'
    )

    # Noise lines
    rng = random.Random(hash(code) % (2 ** 31))
    for _ in range(4):
        x1 = rng.randint(0, width)
        y1 = rng.randint(0, height)
        x2 = rng.randint(0, width)
        y2 = rng.randint(0, height)
        elements.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#cbd5e1" stroke-width="1" stroke-linecap="round"/>'
        )

    # Noise dots
    for _ in range(20):
        cx = rng.randint(0, width)
        cy = rng.randint(0, height)
        elements.append(
            f'<circle cx="{cx}" cy="{cy}" r="1" fill="#94a3b8"/>'
        )

    # Characters
    for i, ch in enumerate(code):
        x = 14 + i * char_width
        y = 34 + rng.randint(-3, 3)
        rotation = rng.randint(-15, 15)
        r, g, b = rng.randint(30, 80), rng.randint(30, 120), rng.randint(100, 200)
        elements.append(
            f'<text x="{x}" y="{y}" '
            f'transform="rotate({rotation} {x} {y})" '
            f'font-family="monospace" font-size="22" font-weight="bold" '
            f'fill="rgb({r},{g},{b})" text-anchor="middle">{ch}</text>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        + "".join(elements)
        + "</svg>"
    )
    return svg


def create_captcha(db: Session) -> tuple[str, str, str]:
    code = generate_code()
    captcha = CaptchaCode.generate(code)
    db.add(captcha)
    db.commit()
    db.refresh(captcha)
    svg = generate_svg(code)
    return captcha.token, code, svg


def verify_captcha(db: Session, token: str, answer: str) -> bool:
    if not token or not answer:
        return False

    captcha = (
        db.query(CaptchaCode)
        .filter(CaptchaCode.token == token, CaptchaCode.is_used == False)
        .first()
    )
    if not captcha:
        return False

    now = datetime.now(timezone.utc)
    if captcha.expires_at.replace(tzinfo=timezone.utc) < now:
        captcha.is_used = True
        db.commit()
        return False

    valid = captcha.code.upper() == answer.upper()
    if valid:
        captcha.is_used = True
        db.commit()
    return valid
