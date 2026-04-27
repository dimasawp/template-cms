from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.dependencies import check_permission
from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role
from app.modules.audit.models.audit_model import AuditLog
from app.helpers.response import success_response
from app.exceptions import handle_errors

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

@router.get("/stats")
@handle_errors
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("users.view")),
):
    """Fetch summary statistics for the dashboard."""
    total_users = db.query(func.count(User.id)).scalar()
    total_roles = db.query(func.count(Role.id)).scalar()
    total_logs = db.query(func.count(AuditLog.id)).scalar()
    
    # Count active users
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    return success_response(data={
        "total_users": total_users,
        "active_users": active_users,
        "total_roles": total_roles,
        "total_logs": total_logs,
        "system_status": "Online"
    })
