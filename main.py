"""Основной файл запуска бота."""
import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs, ShowMode
from redis.asyncio import Redis

from app.config.config import load_config
from app.database.database import Database
from app.infrastructure.redis.redis_manager import RedisManager
from app.infrastructure.google_sheets.sheets_manager import GoogleSheetsManager
from app.middleware import DependencyMiddleware
from app.handlers import router as main_router
from app.dialogs.registry import register_dialogs


async def main():
    """Основная функция запуска бота."""
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("bot.log", encoding="utf-8")
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Загружаем конфигурацию
        config = load_config()
        logger.info("Конфигурация загружена")
        
        # Создаем Redis клиента для FSM
        if config.redis.password:
            redis_url = f"redis://:{config.redis.password}@{config.redis.host}:{config.redis.port}/0"
        else:
            redis_url = f"redis://{config.redis.host}:{config.redis.port}/0"
        
        redis_client = Redis.from_url(redis_url)
        
        # Проверяем подключение к Redis
        try:
            await redis_client.ping()
            logger.info(f"✅ Подключение к Redis установлено: {config.redis.host}:{config.redis.port}")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            return
        
        # Создаем хранилище для FSM
        storage = RedisStorage(
            redis=redis_client,
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True)
        )
        
        # Создаем бота и диспетчер
        bot = Bot(
            token=config.bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher(storage=storage)
        logger.info("Бот и диспетчер созданы")
        
        # Инициализируем базу данных
        database = Database(config.database)
        logger.info("База данных инициализирована")
        
        # Инициализируем Google Sheets
        sheets_manager = None
        try:
            sheets_manager = GoogleSheetsManager(config.google_sheets)
            logger.info("✅ Google Sheets инициализированы")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка инициализации Google Sheets: {e}")
        
        # Настраиваем middleware для передачи зависимостей
        async def services_middleware(handler, event, data):
            async with database.get_session() as session:
                # Создаем сервисы
                from app.services.user_service import UserService
                from app.services.event_service import EventService
                
                user_service = UserService(session, sheets_manager) if sheets_manager else None
                event_service = EventService(session, sheets_manager) if sheets_manager else None
                
                # Добавляем в данные
                data["session"] = session
                data["user_service"] = user_service
                data["event_service"] = event_service
                data["sheets_manager"] = sheets_manager
                
                return await handler(event, data)
        
        # Регистрируем middleware
        dp.message.middleware(services_middleware)
        dp.callback_query.middleware(services_middleware)
        
        # Регистрируем обработчики
        dp.include_router(main_router)
        logger.info("Основные обработчики зарегистрированы")
        
        # Регистрируем диалоги
        register_dialogs(dp)
        logger.info("Диалоги зарегистрированы")
        
        # Настраиваем aiogram-dialog
        setup_dialogs(dp)
        logger.info("aiogram-dialog настроен")
        
        logger.info("🚀 Запуск бота...")
        print("🤖 Бот запущен и готов к работе!")
        
        # Запускаем бота
        try:
            await dp.start_polling(bot)
        finally:
            # Закрываем соединения
            await bot.session.close()
            await database.close()
            await redis_client.aclose()
            logger.info("Соединения закрыты")
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)