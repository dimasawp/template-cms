"""
Global error handler decorator and FastAPI exception handlers.

Usage on controllers:
    @router.get("")
    @handle_errors
    async def get_all_items(...):
        ...
"""

import functools
import logging
import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.helpers.response import error_response


logger = logging.getLogger("cms_template_api")


# ── Decorator for controller endpoints ──────────────────────────────

def handle_errors(func):
    """
    Decorator that wraps a controller endpoint with try/except.
    - HTTPException  → re-raised (FastAPI handles it)
    - Exception      → logged + returns 500
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as exc:
            logger.error(
                f"Unhandled error in {func.__name__}: {exc}",
                exc_info=True,
            )
            return error_response(
                message="Internal server error",
                code=500,
            )

    return wrapper


# ── Global exception handlers (registered in main.py) ───────────────

async def http_exception_handler(request: Request, exc: HTTPException):
    """Convert HTTPException to standard JSON envelope."""
    return error_response(message=str(exc.detail), code=exc.status_code)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors to standard JSON envelope."""
    errors = [
        {"field": ".".join(str(loc) for loc in err["loc"]), "detail": err["msg"]}
        for err in exc.errors()
    ]
    return error_response(message="Validation error", code=422, errors=errors)


async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors."""
    logger.critical(f"Unhandled exception: {exc}", exc_info=True)
    return error_response(message="Internal server error", code=500)
