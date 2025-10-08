"""Middleware для внедрения зависимостей и проверки блокировки."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery, InlineQuery
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
        logger.info(f"LockMiddleware инициализирован. Админы: {admin_ids}")
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем user_id из события (работаем с Update)
        user_id = None
        event_type = type(event).__name__
        
        logger.info(f"LockMiddleware: получено событие {event_type}")
        
        # Извлекаем пользователя из разных типов событий внутри Update
        try:
            if hasattr(event, 'message') and event.message and hasattr(event.message, 'from_user') and event.message.from_user:
                user_id = event.message.from_user.id
                logger.info(f"LockMiddleware: найден user_id {user_id} в event.message.from_user")
            elif hasattr(event, 'callback_query') and event.callback_query and hasattr(event.callback_query, 'from_user') and event.callback_query.from_user:
                user_id = event.callback_query.from_user.id
                logger.info(f"LockMiddleware: найден user_id {user_id} в event.callback_query.from_user")
            elif hasattr(event, 'inline_query') and event.inline_query and hasattr(event.inline_query, 'from_user') and event.inline_query.from_user:
                user_id = event.inline_query.from_user.id
                logger.info(f"LockMiddleware: найден user_id {user_id} в event.inline_query.from_user")
            elif hasattr(event, 'chosen_inline_result') and event.chosen_inline_result and hasattr(event.chosen_inline_result, 'from_user') and event.chosen_inline_result.from_user:
                user_id = event.chosen_inline_result.from_user.id
                logger.info(f"LockMiddleware: найден user_id {user_id} в event.chosen_inline_result.from_user")
            elif hasattr(event, 'from_user') and event.from_user:
                user_id = event.from_user.id
                logger.info(f"LockMiddleware: найден user_id {user_id} в event.from_user")
            else:
                logger.info(f"LockMiddleware: не удалось найти user_id в событии {event_type}")
        except Exception as e:
            logger.error(f"LockMiddleware: ошибка при извлечении user_id: {e}")
        
        logger.info(f"LockMiddleware: обработка {event_type}, пользователь: {user_id}")
        
        # Если не удалось получить user_id, пропускаем (возможно системное событие)
        if user_id is None:
            logger.info(f"LockMiddleware: не удалось получить user_id для события {event_type}, пропускаем")
            return await handler(event, data)
        
        # Если пользователь админ, пропускаем проверку блокировки
        if user_id in self.admin_ids:
            logger.info(f"LockMiddleware: пользователь {user_id} - админ, пропускаем проверку блокировки")
            return await handler(event, data)
        
        # Проверяем блокировку
        try:
            is_locked = await self.lock_service.is_locked()
            logger.info(f"LockMiddleware: состояние блокировки = {is_locked}")
            
            if is_locked:
                logger.warning(f"LockMiddleware: БЛОКИРОВКА АКТИВНА! Блокируем пользователя {user_id}")
                
                # Бот заблокирован, отправляем уведомление о технических работах
                try:
                    # Определяем тип события и отправляем соответствующее уведомление
                    if hasattr(event, 'message') and event.message:
                        await event.message.answer(
                            "🔧 <b>Технические работы</b>\n\n"
                            "В данный момент проводятся технические работы.\n"
                            "Попробуйте воспользоваться ботом позже.\n\n"
                            "Приносим извинения за неудобства! 🙏"
                        )
                        logger.warning(f"LockMiddleware: отправлено уведомление о тех. работах пользователю {user_id}")
                    elif hasattr(event, 'callback_query') and event.callback_query:
                        await event.callback_query.answer(
                            "🔧 Проводятся технические работы. Попробуйте позже.",
                            show_alert=True
                        )
                        logger.warning(f"LockMiddleware: отправлено callback уведомление о тех. работах пользователю {user_id}")
                    elif hasattr(event, 'inline_query') and event.inline_query:
                        # Для inline запросов просто не отвечаем
                        logger.warning(f"LockMiddleware: заблокирован inline запрос от пользователя {user_id}")
                    else:
                        logger.warning(f"LockMiddleware: неподдерживаемый тип события {event_type} для отправки уведомления")
                        
                except Exception as e:
                    logger.error(f"LockMiddleware: ошибка при отправке уведомления о блокировке пользователю {user_id}: {e}")
                
                # Не передаем управление дальше
                logger.warning(f"LockMiddleware: БЛОКИРУЕМ дальнейшую обработку для пользователя {user_id}")
                return None
            
        except Exception as e:
            logger.error(f"LockMiddleware: ошибка при проверке блокировки для пользователя {user_id}: {e}")
            # В случае ошибки Redis - пропускаем запрос дальше (fail-safe)
            logger.warning("LockMiddleware: из-за ошибки Redis пропускаем запрос дальше")
        
        # Бот не заблокирован, продолжаем обработку
        logger.info(f"LockMiddleware: блокировка неактивна, передаем управление дальше для пользователя {user_id}")
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