from sqlalchemy import Column, String, ForeignKey, Table, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.core.database.connection import Base
from src.core.database.base_model import AuditModel

# Join table mapping roles to permissions (Many-to-Many)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

class Role(AuditModel):
    """
    Authorization Roles table config (e.g. ROLE_TELLER, ROLE_ADMIN).
    """
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    key = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", back_populates="role")

class Permission(AuditModel):
    """
    Granular permission items mapping user privileges.
    """
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class User(AuditModel):
    """
    User profile account credentials and statuses.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active, suspended, archived

    # Relationships
    role = relationship("Role", back_populates="users")

class UserRefreshToken(AuditModel):
    """
    Stores active user session refresh tokens for validation and revocation.
    """
    __tablename__ = "user_refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(512), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, nullable=False, default=False)

    # Relationships
    user = relationship("User")

