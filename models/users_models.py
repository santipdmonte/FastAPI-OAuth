from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Text, DateTime, func
from typing import Optional
from uuid import UUID
from enum import Enum
from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
import uuid

class AuthProviderType(str, Enum):
    """Tipos de proveedores de autenticación."""
    EMAIL = "email"
    GOOGLE = "google"
    # ... More providers can be added here

class Base(DeclarativeBase):
    pass

class User(Base):
    """Modelo de usuario con mejores prácticas para SQLAlchemy v2."""
    
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),  
        index=True, 
        unique=True, 
        nullable=False
    )
    
    full_name: Mapped[str] = mapped_column(String(200), nullable=True)
    given_name: Mapped[str] = mapped_column(String(100), nullable=True)
    family_name: Mapped[str] = mapped_column(String(100), nullable=True)
    picture: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    social_accounts: Mapped[list["UserSocialAccount"]] = relationship(
        "UserSocialAccount", back_populates="user"
    ) 

    def __repr__(self) -> str:
        """Representación legible del objeto."""
        return f"<User(id={self.id}, email='{self.email}', email='{self.email}')>"

    def __str__(self) -> str:
        """String representation para usuarios."""
        return self.full_name or self.email

    @property
    def is_active(self) -> bool:
        """Verifica si el usuario está activo."""
        return not self.disabled


class UserSocialAccount(Base):
    """Identidades de autenticación de usuarios (emails, OAuth accounts)."""
    
    __tablename__ = "user_social_accounts"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    provider: Mapped[AuthProviderType] = mapped_column(String(20), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    given_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    family_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    picture: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    last_used: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    user: Mapped["User"] = relationship("User", back_populates="social_accounts")

    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="uq_provider_social_account"),
        Index("idx_provider_lookup", "provider", "provider_id"),
    )

    def __repr__(self) -> str:
        return f"<UserSocialAccount(provider='{self.provider}', provider_id='{self.provider_id}')>"

    def mark_as_verified(self) -> None:
        """Marcar identidad como verificada."""
        self.is_verified = True

    def update_last_used(self) -> None:
        """Actualizar último uso."""
        self.last_used = datetime.now(timezone.utc)
