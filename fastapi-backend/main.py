"""
CMS Template API — Main Entry Point

Run: uvicorn main:app --reload
"""

import logging
import uuid
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.logger import setup_logger, log_error
from app.modules import register_all_routers
from app.exceptions.handler import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)


# ── App Instance ─────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False,
    },
    swagger_ui_parameters={
        "persistAuthorization": True,
        "docExpansion": "none"
    },
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/storage", StaticFiles(directory=settings.UPLOAD_DIR), name="storage")

# ── Logging ──────────────────────────────────────────────────────────

setup_logger(
    log_dir=settings.LOG_DIR,
    max_bytes=settings.LOG_MAX_BYTES,
    backup_count=settings.LOG_BACKUP_COUNT,
)


# ── Global Exception Handlers ───────────────────────────────────────

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# ── Request Logging Middleware ───────────────────────────────────────

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    method = request.method
    path = request.url.path
    client_ip = request.client.host if request.client else "unknown"

    response = await call_next(request)

    if response.status_code >= 500:
        log_error(
            message=f"{method} {path} -> {response.status_code}",
            method=method, path=path, status_code=response.status_code,
            client_ip=client_ip, request_id=request_id,
            level=logging.ERROR,
        )
    elif response.status_code >= 400:
        log_error(
            message=f"{method} {path} -> {response.status_code}",
            method=method, path=path, status_code=response.status_code,
            client_ip=client_ip, request_id=request_id,
            level=logging.WARNING,
        )

    response.headers["X-Request-ID"] = request_id
    return response


# ── Health Checks ────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/db-test")
async def db_test():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()")).fetchone()
        return {"database": "connected", "db_name": result[0]}
    except Exception as e:
        return {"database": "disconnected", "error": str(e)}


# ── Auto-Register Module Routers ────────────────────────────────────

register_all_routers(app)


# ── Run directly ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
