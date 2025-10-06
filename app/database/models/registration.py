"""Модель мероприятий и регистраций."""
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EventType(Enum):
    """Типы мероприятий."""
    PLENARY = "plenary"  # Пленарная сессия
    SPEECH = "speech"    # Выступление
    WORKSHOP = "workshop"  # Воркшоп/сессия


class Event(Base):
    """Модель мероприятия."""
    
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    start_time: Mapped[str] = mapped_column(String(20), nullable=False)  # "11:00"
    end_time: Mapped[str] = mapped_column(String(20), nullable=False)    # "12:40"
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_exclusive: Mapped[bool] = mapped_column(default=False)  # Взаимоисключающие мероприятия
    max_participants: Mapped[int] = mapped_column(nullable=True)  # Максимальное количество участников
    sheet_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Название листа в Google Sheets
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Связь с регистрациями
    registrations: Mapped[list["EventRegistration"]] = relationship(
        "EventRegistration", 
        back_populates="event",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Event(name={self.name}, time={self.start_time}-{self.end_time})>"


class EventRegistration(Base):
    """Модель регистрации пользователя на мероприятие."""
    
    __tablename__ = "event_registrations"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("events.id"), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Связи - используем строковые ссылки для избежания циклических импортов
    user: Mapped["User"] = relationship("User", back_populates="registrations")
    event: Mapped["Event"] = relationship("Event", back_populates="registrations")
    
    # Уникальность регистрации: один пользователь может зарегистрироваться на мероприятие только один раз
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="unique_user_event"),
    )
    
    def __repr__(self) -> str:
        return f"<EventRegistration(user_id={self.user_id}, event_id={self.event_id})>"