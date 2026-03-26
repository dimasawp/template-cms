"""
Lightweight email helper using aiosmtplib + Jinja2 templates.

Usage::
    from app.helpers.email import send_email

    await send_email(
        to="user@example.com",
        subject="Welcome!",
        template="welcome.html",
        context={"name": "John"},
    )
"""

import os
from typing import Optional, Dict, Any
from email.message import EmailMessage

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings

_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates", "email")
_jinja_env: Optional[Environment] = None


def _get_jinja_env() -> Environment:
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = Environment(
            loader=FileSystemLoader(os.path.abspath(_TEMPLATE_DIR)),
            autoescape=True,
        )
    return _jinja_env


async def send_email(
    *,
    to: str,
    subject: str,
    template: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    body_plain: Optional[str] = None,
    body_html: Optional[str] = None,
) -> None:
    msg = EmailMessage()
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to
    msg["Subject"] = subject

    if template:
        env = _get_jinja_env()
        tmpl = env.get_template(template)
        html = tmpl.render(**(context or {}))
        msg.set_content(html, subtype="html")
    elif body_html:
        msg.set_content(body_html, subtype="html")
    elif body_plain:
        msg.set_content(body_plain)
    else:
        msg.set_content("(no content)")

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER or None,
        password=settings.SMTP_PASSWORD or None,
        use_tls=settings.SMTP_USE_TLS,
    )
