# Модели базы данных
from .base import Base
from .user import User
from .registration import Event, EventRegistration

# Экспортируем все модели
__all__ = ["Base", "User", "Event", "EventRegistration"]