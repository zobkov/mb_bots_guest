"""Middleware для внедрения зависимостей."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import Database
from app.infrastructure.google_sheets.sheets_manager import GoogleSheetsManager
from app.services.user_service import UserService
from app.services.event_service import EventService


class DependencyMiddleware(BaseMiddleware):
    """Middleware для внедрения зависимостей в обработчики."""
    
    def __init__(
        self,
        database: Database,
        sheets_manager: GoogleSheetsManager
    ):
        self.database = database
        self.sheets_manager = sheets_manager
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.database.get_session() as session:
            # Создаем сервисы
            user_service = UserService(session, self.sheets_manager)
            event_service = EventService(session, self.sheets_manager)
            
            # Добавляем в данные
            data["session"] = session
            data["user_service"] = user_service
            data["event_service"] = event_service
            data["sheets_manager"] = self.sheets_manager
            
            return await handler(event, data)