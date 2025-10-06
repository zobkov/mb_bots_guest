"""Подключение к базе данных."""
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config.config import DatabaseConfig


class Database:
    """Класс для управления подключением к базе данных."""
    
    def __init__(self, config: DatabaseConfig):
        # Используем psycopg для асинхронной работы
        self.engine = create_async_engine(
            config.url,
            echo=False,
            future=True
        )
        
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получить сессию базы данных как async context manager."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Закрыть соединение с базой данных."""
        await self.engine.dispose()