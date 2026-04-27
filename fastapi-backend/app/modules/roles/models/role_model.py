from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(),
        onupdate=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(),
        nullable=False,
    )
    deleted_at = Column(DateTime, nullable=True)

    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: __import__('app.helpers.date_helper', fromlist=['get_now_wib']).get_now_wib(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.name}>"
