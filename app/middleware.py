"""Middleware для внедрения зависимостей и проверки блокировки."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery
import redis.asyncio as redis

from app.database.database import Database
from app.infrastructure.google_sheets.sheets_manager import GoogleSheetsManager
from app.services.user_service import UserService
from app.services.event_service import EventService
from app.services.lock_service import LockService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LockMiddleware(BaseMiddleware):
    """Middleware для проверки блокировки бота."""
    
    def __init__(self, redis_client: redis.Redis, admin_ids: list[int]):
        self.lock_service = LockService(redis_client)
        self.admin_ids = admin_ids
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем user_id из события
        user_id = None
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message and event.message.from_user:
            user_id = event.message.from_user.id
        
        # Если пользователь админ, пропускаем проверку блокировки
        if user_id in self.admin_ids:
            return await handler(event, data)
        
        # Проверяем блокировку
        is_locked = await self.lock_service.is_locked()
        if is_locked:
            # Бот заблокирован, отправляем уведомление о технических работах
            try:
                if isinstance(event, Message):
                    await event.answer(
                        "🔧 <b>Технические работы</b>\n\n"
                        "В данный момент проводятся технические работы.\n"
                        "Попробуйте воспользоваться ботом позже.\n\n"
                        "Приносим извинения за неудобства! 🙏"
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "🔧 Проводятся технические работы. Попробуйте позже.",
                        show_alert=True
                    )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления о блокировке: {e}")
            
            # Не передаем управление дальше
            return
        
        # Бот не заблокирован, продолжаем обработку
        return await handler(event, data)


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