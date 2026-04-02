"""
CMS Template API — Main Entry Point

Run: uvicorn main:app --reload
"""

import logging
import uuid
import os

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import time

# --- Import models to populate SQLAlchemy registry ---
from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role
from app.modules.audit.models.audit_model import AuditLog
# -----------------------------------------------------

from app.core.database import engine, Base
from fastapi.responses import JSONResponse
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
from app.core.websocket import manager


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


# ── Maintenance Mode Middleware ─────────────────────────────────────

@app.middleware("http")
async def maintenance_mode_middleware(request: Request, call_next):
    # Skip for documentation, static files, and login/me endpoints
    path = request.url.path
    exempt_paths = [
        "/", "/db-test", "/docs", "/redoc", "/openapi.json",
        "/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/auth/swagger-login",
        "/api/v1/auth/logout", "/api/v1/auth/refresh", "/api/v1/auth/me",
        "/api/v1/settings" # Allow fetching settings (to check maintenance status in FE)
    ]
    
    if any(path.startswith(p) for p in exempt_paths) or path.startswith("/storage"):
        return await call_next(request)

    # Check database for maintenance_mode setting
    from app.modules.settings.models.setting_model import Setting
    from app.core.database import SessionLocal
    from app.core.security import decode_token
    from datetime import datetime
    
    db = SessionLocal()
    try:
        # Get settings
        settings_rows = db.query(Setting).filter(Setting.setting_key.in_(["maintenance_mode", "maintenance_scheduled_at"])).all()
        s_dict = {s.setting_key: s.setting_value for s in settings_rows}
        
        maintenance_active = s_dict.get("maintenance_mode") == "true"
        scheduled_at = s_dict.get("maintenance_scheduled_at")
        
        should_block = maintenance_active
        if maintenance_active and scheduled_at:
            try:
                # Expecting ISO format from frontend (e.g. 2024-03-31T20:55:00.000Z)
                target_dt = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
                now_dt = datetime.now(target_dt.tzinfo)
                if now_dt < target_dt:
                    should_block = False # Not yet time
            except (ValueError, TypeError):
                pass
        
        if should_block:
            # Check for super_admin bypass
            is_superadmin = False
            auth_header = request.headers.get("Authorization")
            
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                if payload and payload.get("type") == "access":
                    try:
                        user_id = int(payload.get("sub"))
                        # Raw SQL case-insensitive check
                        from sqlalchemy import text
                        sql = text("SELECT LOWER(r.name) FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = :uid AND u.is_active = 1")
                        res = db.execute(sql, {"uid": user_id}).fetchone()
                        if res and res[0] in ["super_admin", "superadmin", "admin"]:
                            is_superadmin = True
                    except (ValueError, TypeError):
                        pass
            
            if not is_superadmin:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "error",
                        "message": "System is under maintenance. Only administrators can access the API at this time.",
                        "debug_info": "Maintenance: ON, Admin Check: Failed",
                        "code": "MAINTENANCE_MODE"
                    }
                )
    except Exception as e:
        # If anything fails in the middleware, we fallback to ALLOWING for now
        # to prevent complete system lockout if there is a bug
        print(f"MIDDLEWARE ERROR: {e}")
        pass
    finally:
        db.close()

    return await call_next(request)


# ── WebSocket Notifications — Real-time Updates ─────────────────────

@app.websocket("/api/v1/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    if not settings.ENABLE_WEBSOCKETS:
        await websocket.close(code=1003) # Unsupported Data
        return

    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, though we mainly broadcast from server
            data = await websocket.receive_text()
            # We can handle client messages here if needed (e.g. "ACK")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


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
