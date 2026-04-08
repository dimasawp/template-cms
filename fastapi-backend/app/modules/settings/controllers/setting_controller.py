from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Dict

from app.modules.users.models.user_model import User

from app.core.database import get_db
from app.core.dependencies import require_roles, check_permission
from app.modules.settings.schemas.setting_schema import SettingResponse, SettingUpdate, SettingBulkUpdate
from app.modules.settings.services.setting_service import SettingService
from app.helpers.response import success_response
from app.exceptions import handle_errors


router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


@router.get("")
@handle_errors
async def get_all_settings(db: Session = Depends(get_db)):
    """Akses publik / terbuka untuk ambil konfigurasi web"""
    from app.core.config import settings as app_settings
    settings_dict = SettingService.get_all(db, as_dict=True)
    
    # Inject backend config flags
    settings_dict["enable_websockets"] = app_settings.ENABLE_WEBSOCKETS
    settings_dict["app_version"] = app_settings.APP_VERSION
    
    return success_response(data=settings_dict)


@router.get("/raw")
@handle_errors
async def get_raw_settings(
    db: Session = Depends(get_db),
    _=Depends(check_permission("settings.view"))
):
    """Ambil list settings mentah (butuh akses Admin)"""
    settings = SettingService.get_all(db, as_dict=False)
    return success_response(data=settings)


@router.put("/{key}")
@handle_errors
async def update_setting(
    key: str,
    payload: SettingUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permission("settings.update"))
):
    """Update satu jenis setting (hanya Super Admin)"""
    setting = SettingService.update_setting(db, key, payload.setting_value, payload.description)
    return success_response(data=setting, message=f"Setting '{key}' updated successfully")


@router.post("/bulk")
@handle_errors
async def bulk_update_settings(
    payload: SettingBulkUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("settings.update"))
):
    """Update banyak setting sekaligus (hanya Super Admin)"""
    settings = SettingService.bulk_update(
        db, payload.settings, 
        user_id=current_user.id, 
        request=request
    )
    
    # ── Broadcast Update via WebSocket ──────────────────────────────
    from app.core.websocket import manager
    from app.core.config import settings as app_settings
    
    if app_settings.ENABLE_WEBSOCKETS:
        # Check if maintenance settings were involved
        m_keys = ["maintenance_mode", "maintenance_scheduled_at"]
        if any(item.setting_key in m_keys for item in payload.settings):
            # Fetch latest dict to broadcast
            latest_dict = SettingService.get_all(db, as_dict=True)
            await manager.broadcast({
                "type": "MAINTENANCE_UPDATE",
                "payload": {
                    "maintenance_mode": latest_dict.get("maintenance_mode"),
                    "maintenance_scheduled_at": latest_dict.get("maintenance_scheduled_at")
                }
            })

    return success_response(data=settings, message="Settings updated successfully")
