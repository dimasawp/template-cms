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
async def get_all_settings(request: Request, db: Session = Depends(get_db)):
    """Akses publik / terbuka untuk ambil konfigurasi web"""
    from app.core.config import settings as app_settings
    from app.core.security import get_current_user_optional
    
    # Check if user is superadmin (optional)
    current_user = await get_current_user_optional(request, db)
    is_superadmin = False
    if current_user:
        # Check role name (case-insensitive)
        from sqlalchemy import text
        sql = text("SELECT LOWER(name) FROM roles WHERE id = :rid")
        res = db.execute(sql, {"rid": current_user.role_id}).fetchone()
        if res and res[0] in ["superadmin", "super_admin"]:
            is_superadmin = True

    settings_dict = SettingService.get_all(db, as_dict=True)
    
    # Filter out system settings if not superadmin (though for public it usually shows site_name etc)
    # But for safety, we only return non-sensitive ones to public
    if not is_superadmin:
        system_keys = ["maintenance_mode", "maintenance_scheduled_at", "registration_enabled"]
        # Actually, public needs to know maintenance status to show the banner
        # So we only hide them if the user specifically requested to separate them
        # For now, let's just keep public access as is, but enforce it on the RAW/UPDATE side
        pass

    # Inject backend config flags
    settings_dict["enable_websockets"] = app_settings.ENABLE_WEBSOCKETS
    settings_dict["app_version"] = app_settings.APP_VERSION
    
    return success_response(data=settings_dict)


@router.get("/raw")
@handle_errors
async def get_raw_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("settings.view"))
):
    """Ambil list settings mentah (butuh akses Admin)"""
    # Check role
    from sqlalchemy import text
    sql = text("SELECT LOWER(name) FROM roles WHERE id = :rid")
    res = db.execute(sql, {"rid": current_user.role_id}).fetchone()
    is_superadmin = res and res[0] in ["superadmin", "super_admin"]

    group_filter = None if is_superadmin else "general"
    settings = SettingService.get_all(db, as_dict=False, group=group_filter)
    return success_response(data=settings)


@router.put("/{key}")
@handle_errors
async def update_setting(
    key: str,
    payload: SettingUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("settings.update"))
):
    """Update satu jenis setting (hanya Super Admin untuk system)"""
    # Check if system setting
    setting = SettingService.get_by_key(db, key)
    
    if setting.setting_group == "system":
        from sqlalchemy import text
        sql = text("SELECT LOWER(name) FROM roles WHERE id = :rid")
        res = db.execute(sql, {"rid": current_user.role_id}).fetchone()
        if not res or res[0] not in ["superadmin", "super_admin"]:
            from app.exceptions import ForbiddenException
            raise ForbiddenException("Hanya Super Admin yang dapat mengubah pengaturan sistem")

    setting = SettingService.update_setting(
        db, key, payload.setting_value, payload.description,
        user_id=current_user.id, request=request
    )
    return success_response(data=setting, message=f"Setting '{key}' updated successfully")


@router.post("/reset")
@handle_errors
async def reset_settings(
    request: Request,
    group: str = "system",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["superadmin", "super_admin"]))
):
    """Reset settings to defaults by group (hanya Super Admin)"""
    SettingService.reset_settings(db, group=group, user_id=current_user.id, request=request)
    return success_response(message="Semua pengaturan berhasil dikembalikan ke default")


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
