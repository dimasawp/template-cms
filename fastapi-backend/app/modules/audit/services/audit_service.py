from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, Dict, Any
from fastapi import Request

from app.modules.audit.models.audit_model import AuditLog


class AuditService:

    @staticmethod
    def log(
        db: Session,
        user_id: Optional[int],
        action: str,
        module: str,
        item_id: Optional[str] = None,
        description: Optional[str] = None,
        payload_before: Optional[Dict[str, Any]] = None,
        payload_after: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Record an activity log."""
        ip_addr = None
        user_agent = None
        
        if request:
            ip_addr = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")[:255] if request.headers.get("user-agent") else None

        new_log = AuditLog(
            user_id=user_id,
            action=action,
            module=module,
            item_id=item_id,
            description=description,
            payload_before=payload_before,
            payload_after=payload_after,
            ip_address=ip_addr,
            user_agent=user_agent
        )
        db.add(new_log)
        db.commit()
        return new_log

    @staticmethod
    def get_logs(
        db: Session, 
        limit: int = 50, 
        offset: int = 0, 
        module: str = None, 
        user_id: int = None,
        action: str = None,
        search: str = None,
        order_by: str = "created_at",
        order_dir: str = "desc"
    ):
        """Retrieve paginated audit logs."""
        query = db.query(AuditLog)
        
        if module:
            query = query.filter(AuditLog.module == module)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action.ilike(f"%{action}%"))
        if search:
            query = query.filter(
                (AuditLog.description.ilike(f"%{search}%")) |
                (AuditLog.action.ilike(f"%{search}%")) |
                (AuditLog.module.ilike(f"%{search}%"))
            )
            
        # Sorting
        sort_col = getattr(AuditLog, order_by, AuditLog.created_at)
        if order_dir.lower() == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())
            
        total = query.count()
        logs = query.offset(offset).limit(limit).all()
        return logs, total
