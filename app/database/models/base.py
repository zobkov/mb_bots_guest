"""Базовая модель для всех моделей базы данных."""
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# Создаем базовый класс для всех моделей
metadata = MetaData()
Base = declarative_base(metadata=metadata)