from sqlalchemy.orm import Session
from typing import List, Dict
from app.modules.settings.models.setting_model import Setting
from app.modules.settings.schemas.setting_schema import SettingBase
from app.exceptions import NotFoundException
from app.modules.audit.services.audit_service import AuditService
from fastapi import Request


class SettingService:

    @staticmethod
    def get_all(db: Session, as_dict: bool = False):
        settings = db.query(Setting).all()
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
    def update_setting(db: Session, key: str, value: str, description: str = None) -> Setting:
        setting = db.query(Setting).filter(Setting.setting_key == key).first()
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
            db=db, user_id=user_id, action="SETTINGS_UPDATE", module="SETTINGS",
            description="User updated global system settings",
            payload_before=payload_before, payload_after=payload_after,
            request=request
        )

        return results
