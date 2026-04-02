from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from app.core.database import get_db
from app.core.dependencies import require_roles, check_permission
from app.modules.audit.schemas.audit_schema import AuditLogResponse
from app.modules.audit.services.audit_service import AuditService
from app.helpers.response import success_response, paginated_response
from app.exceptions import handle_errors


router = APIRouter(prefix="/api/v1/audit", tags=["Audit Logs"])


@router.get("", response_model=Dict)
@handle_errors
async def get_audit_logs(
    per_page: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1),
    module: str = Query(None),
    user_id: int = Query(None),
    action: str = Query(None),
    search: str = Query(None),
    order_by: str = Query("created_at"),
    order_dir: str = Query("desc"),
    db: Session = Depends(get_db),
    _=Depends(check_permission("audit.view"))
):
    """Retrieve audit logs with filtering and sorting (Super Admin only)."""
    offset = (page - 1) * per_page
    logs, total = AuditService.get_logs(
        db, limit=per_page, offset=offset, 
        module=module, user_id=user_id, action=action,
        search=search, order_by=order_by, order_dir=order_dir
    )
    
    # Convert SQLAlchemy objects to Pydantic-validated dicts
    items = [AuditLogResponse.model_validate(l).model_dump() for l in logs]
    
    return paginated_response(items=items, total=total, page=page, per_page=per_page)


@router.get("/modules")
@handle_errors
async def get_audit_modules(
    db: Session = Depends(get_db),
    _=Depends(check_permission("audit.view"))
):
    """Retrieve unique modules from audit logs for filtering."""
    from app.modules.audit.models.audit_model import AuditLog
    modules = db.query(AuditLog.module).distinct().all()
    return success_response(data=[m[0] for m in modules])
