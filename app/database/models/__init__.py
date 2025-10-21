# Модели базы данных
from .base import Base
from .user import User
from .registration import Event, EventRegistration
from .passport import PassportData

# Экспортируем все модели
__all__ = ["Base", "User", "Event", "EventRegistration", "PassportData"]