from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from datetime import datetime, timedelta, timezone

from app.modules.users.models.user_model import User
from app.modules.roles.models.role_model import Role
from app.modules.auth.models.session_model import UserSession
from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
)
from app.modules.auth.schemas.auth_schema import TokenResponse
from app.exceptions import UnauthorizedException, ForbiddenException, NotFoundException
from app.modules.audit.services.audit_service import AuditService
from app.modules.settings.services.setting_service import SettingService


class AuthService:

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username, User.deleted_at == None).first()
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Incorrect username or password")
        if not user.is_active:
            raise ForbiddenException("User account is inactive")
        
        from app.helpers.date_helper import get_now_wib
        user.last_login_at = get_now_wib()
        db.commit()
        
        return user

    @staticmethod
    def register_user(db: Session, username: str, email: str, full_name: str, password: str) -> User:
        """Self-registration for new users. Default role is 'viewer'."""
        # Check if username exists
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Check if email exists
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Default role for self-registered users (admin role)
        role = db.query(Role).filter(Role.name == "admin").first()
        if not role:
            raise HTTPException(status_code=500, detail="Default registration role 'admin' not found")

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
            role_id=role.id,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def create_tokens(user_id: int, request: Request, db: Session) -> TokenResponse:
        import uuid
        
        # Prepare session first with a placeholder for the token to get the ID
        from app.helpers.date_helper import get_now_wib
        ip_addr = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent")[:255] if request and request.headers.get("user-agent") else None
        expires_at = get_now_wib() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_session = UserSession(
            user_id=user_id,
            refresh_token=f"tmp_{uuid.uuid4()}", # Constraint: nullable=False
            ip_address=ip_addr,
            user_agent=user_agent,
            expires_at=expires_at
        )
        db.add(new_session)
        db.flush() # Get the session ID

        # Generate tokens including sid (Session ID)
        access_token = create_access_token(data={"sub": str(user_id), "sid": new_session.id})
        refresh_token = create_refresh_token(data={"sub": str(user_id), "sid": new_session.id})

        # Update session with the real refresh token
        new_session.refresh_token = refresh_token
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid or expired refresh token")

        try:
            user_id = int(payload.get("sub"))
        except (ValueError, TypeError):
            raise UnauthorizedException("Invalid token payload")

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        # Verify refresh token in DB
        from app.helpers.date_helper import get_now_wib
        session = db.query(UserSession).filter(UserSession.refresh_token == refresh_token, UserSession.user_id == user_id).first()
        if not session or session.expires_at < get_now_wib():
            raise UnauthorizedException("Session invalid or expired")

        # Update existing session with new refresh token and expiry
        import uuid
        from app.helpers.date_helper import get_now_wib
        expires_at = get_now_wib() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # We need to temporarily change the refresh_token to avoid unique constraint 
        # if the new one happened to be the same (unlikely with JWT but good practice)
        old_token = session.refresh_token
        session.refresh_token = f"refreshing_{uuid.uuid4()}"
        db.flush()

        # Generate new tokens with the SAME sid
        access_token = create_access_token(data={"sub": str(user_id), "sid": session.id})
        refresh_token = create_refresh_token(data={"sub": str(user_id), "sid": session.id})

        # Update session with the real new refresh token
        session.refresh_token = refresh_token
        session.expires_at = expires_at
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @staticmethod
    def get_user_info(db: Session, user_id: int) -> dict:
        user = db.query(User).filter(User.id == user_id, User.deleted_at == None).first()
        if not user:
            raise NotFoundException("User not found")

        role = db.query(Role).filter(Role.id == user.role_id).first()
        permissions = [p.name for p in role.permissions] if role else []

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role_name": role.name if role else None,
            "permissions": permissions,
            "is_active": user.is_active,
            "avatar": user.avatar,
        }

    @staticmethod
    def update_user_profile(db: Session, user_id: int, username: str = None, full_name: str = None, email: str = None):
        """Update personal profile data."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
        
        # Capture current state for Audit
        payload_before = {"username": user.username, "full_name": user.full_name, "email": user.email}
        
        if username is not None and username != user.username:
            # Check global policy for username change
            try:
                setting = SettingService.get_by_key(db, "allow_username_change")
                if setting.setting_value == "false":
                    raise HTTPException(status_code=403, detail="Username change is disabled by global policy")
            except HTTPException as e:
                if e.status_code == 404:
                    # Setting not found, we can decide to allow or disallow. 
                    # Let's allow by default if the setting is missing.
                    pass
                else:
                    raise e
            except Exception:
                # Other errors, just pass to be safe
                pass

            # Check for uniqueness
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = username

        if full_name is not None:
            user.full_name = full_name
        if email is not None:
            user.email = email
            
        db.commit()
        db.refresh(user)

        # Log activity
        payload_after = {"username": user.username, "full_name": user.full_name, "email": user.email}
        AuditService.log(
            db=db, user_id=user_id, action="UPDATE_PROFILE", module="AUTH",
            item_id=str(user_id), description="User updated their personal profile",
            payload_before=payload_before, payload_after=payload_after
        )

        return user

    @staticmethod
    def change_user_password(db: Session, user_id: int, old_password: str, new_password: str):
        """Verify old password and set new password."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
            
        if not verify_password(old_password, user.password_hash):
            raise UnauthorizedException("Incorrect old password")
            
        user.password_hash = get_password_hash(new_password)
        db.commit()

        # Log activity
        AuditService.log(
            db=db, user_id=user_id, action="CHANGE_PASSWORD", module="AUTH",
            item_id=str(user_id), description="User changed their own password"
        )

        return True

    @staticmethod
    def update_avatar(db: Session, user_id: int, avatar_path: str):
        """Update user avatar path."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
        
        user.avatar = avatar_path
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_all_sessions(db: Session):
        """List all active sessions with user details."""
        return db.query(UserSession).join(User).order_by(UserSession.created_at.desc()).all()

    @staticmethod
    def revoke_session(db: Session, session_id: int):
        """Delete a specific session by ID."""
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if not session:
            raise NotFoundException("Session not found")
        db.delete(session)
        db.commit()
        return True

    @staticmethod
    def bulk_revoke_sessions(db: Session, session_ids: list[int]):
        """Delete multiple sessions by IDs."""
        db.query(UserSession).filter(UserSession.id.in_(session_ids)).delete(synchronize_session=False)
        db.commit()
        return True
