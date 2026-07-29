from sqlalchemy.orm import Session
from typing import List, Dict
from app.modules.settings.models.setting_model import Setting
from app.modules.settings.schemas.setting_schema import SettingBase
from app.exceptions import NotFoundException
from app.modules.audit.services.audit_service import AuditService
from fastapi import Request


class SettingService:

    @staticmethod
    def get_all(db: Session, as_dict: bool = False, group: str = None):
        query = db.query(Setting)
        if group:
            query = query.filter(Setting.setting_group == group)
        
        settings = query.all()
        if as_dict:
            return {s.setting_key: s.setting_value for s in settings}
        return settings

    @staticmethod
    def get_by_key(db: Session, key: str) -> Setting:
        setting = db.query(Setting).filter(Setting.setting_key == key).first()
        if not setting:
            raise NotFoundException(f"Setting '{key}' not found")
        return setting

    @staticmethod
    def update_setting(db: Session, key: str, value: str, description: str = None, user_id: int = None, request: Request = None) -> Setting:
        setting = db.query(Setting).filter(Setting.setting_key == key).first()
        
        payload_before = {key: setting.setting_value if setting else None}

        if not setting:
            setting = Setting(setting_key=key, setting_value=value, description=description)
            db.add(setting)
        else:
            if value is not None:
                setting.setting_value = value
            if description is not None:
                setting.description = description
        db.commit()
        db.refresh(setting)

        # Audit Log
        payload_after = {key: value}
        AuditService.log(
            db=db, user_id=user_id, action="UPDATE", module="SETTINGS",
            description=f"Updated setting: {key}",
            payload_before=payload_before, payload_after=payload_after,
            request=request
        )

        return setting

    @staticmethod
    def bulk_update(db: Session, payload: List[SettingBase], user_id: int = None, request: Request = None):
        results = []
        
        # Capture state before
        payload_before = {}
        for item in payload:
            existing = db.query(Setting).filter(Setting.setting_key == item.setting_key).first()
            payload_before[item.setting_key] = existing.setting_value if existing else None

        for item in payload:
            setting = db.query(Setting).filter(Setting.setting_key == item.setting_key).first()
            if not setting:
                setting = Setting(
                    setting_key=item.setting_key,
                    setting_value=item.setting_value,
                    description=item.description
                )
                db.add(setting)
            else:
                setting.setting_value = item.setting_value
                if item.description is not None:
                    setting.description = item.description
            results.append(setting)
        
        db.commit()
        for r in results:
            db.refresh(r)
            
        # Log activity
        payload_after = {item.setting_key: item.setting_value for item in payload}
        AuditService.log(
            db=db, user_id=user_id, action="UPDATE", module="SETTINGS",
            description="User updated global system settings",
            payload_before=payload_before, payload_after=payload_after,
            request=request
        )

        return results
    @staticmethod
    def reset_settings(db: Session, group: str = "system", user_id: int = None, request: Request = None):
        """Reset settings within a specific group to system defaults."""
        # 1. Capture state before (only for that group)
        settings_before = db.query(Setting).filter(Setting.setting_group == group).all()
        payload_before = {s.setting_key: s.setting_value for s in settings_before}

        # 2. Define defaults
        defaults = [
            {"key": "site_name", "value": "CMS Template", "group": "system", "desc": "Nama aplikasi web"},
            {"key": "maintenance_mode", "value": "false", "group": "system", "desc": "Mode perbaikan"},
            {"key": "maintenance_scheduled_at", "value": "", "group": "system", "desc": "Waktu mulai maintenance"},
            {"key": "contact_email", "value": "admin@example.com", "group": "system", "desc": "Email dukungan sistem"},
            {"key": "enable_user_avatars", "value": "true", "group": "system", "desc": "Izinkan upload foto profil"},
            {"key": "allow_username_change", "value": "true", "group": "system", "desc": "Izinkan ganti username mandiri"},
            {"key": "registration_enabled", "value": "true", "group": "system", "desc": "Izinkan pendaftaran mandiri"},
            {"key": "captcha_enabled", "value": "false", "group": "system", "desc": "Aktifkan CAPTCHA pada login/register"},
            {"key": "category_max_level", "value": "3", "group": "system", "desc": "Maksimal Level Kategori (Nesting)"}
        ]

        # 3. Filter defaults by group
        target_defaults = [d for d in defaults if d["group"] == group]

        # 4. Apply defaults
        for item in target_defaults:
            setting = db.query(Setting).filter(Setting.setting_key == item["key"]).first()
            if not setting:
                setting = Setting(
                    setting_key=item["key"],
                    setting_value=item["value"],
                    setting_group=item["group"],
                    description=item["desc"]
                )
                db.add(setting)
            else:
                setting.setting_value = item["value"]
                setting.setting_group = item["group"]
                setting.description = item["desc"]
        
        db.commit()

        # 5. Log activity
        payload_after = {item["key"]: item["value"] for item in target_defaults}
        AuditService.log(
            db=db, user_id=user_id, action="RESET", module="SETTINGS",
            description=f"User reset global settings for group: {group}",
            payload_before=payload_before, payload_after=payload_after,
            request=request
        )

        return True
