"""Модель пользователя."""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import BigInteger, String, DateTime, func, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .registration import EventRegistration

from .base import Base


class User(Base):
    """Модель пользователя."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=True)  # Telegram username
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    workplace: Mapped[str] = mapped_column(String(500), nullable=False)
    referral_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    referrer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    referral_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    referral_joined_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Связь с регистрациями на мероприятия - используем строковую ссылку
    registrations: Mapped[List["EventRegistration"]] = relationship(
        "EventRegistration", 
        back_populates="user",
        cascade="all, delete-orphan"
    )

    referrer: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side="User.id",
        back_populates="referrals",
    )
    referrals: Mapped[List["User"]] = relationship(
        "User",
        back_populates="referrer",
        cascade="save-update, merge"
    )
    
    def __repr__(self) -> str:
        return f"<User(telegram_id={self.telegram_id}, name={self.first_name} {self.last_name})>"