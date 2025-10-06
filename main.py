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
from aiogram_dialog import setup_dialogs
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
        
        # Создаем бота
        bot = Bot(
            token=config.bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        logger.info("Бот создан")
        
        # Создаем диспетчер
        dp = Dispatcher()
        
        # Инициализируем базу данных
        database = Database(config.database)
        logger.info("База данных инициализирована")
        
        # Инициализируем Redis
        redis_manager = RedisManager(config.redis)
        redis_client = await redis_manager.get_redis()
        logger.info("Redis подключен")
        
        # Инициализируем Google Sheets
        sheets_manager = GoogleSheetsManager(config.google_sheets)
        logger.info("Google Sheets инициализированы")
        
        # Настраиваем middleware
        dependency_middleware = DependencyMiddleware(database, sheets_manager)
        dp.message.middleware(dependency_middleware)
        dp.callback_query.middleware(dependency_middleware)
        
        # Регистрируем обработчики
        dp.include_router(main_router)
        logger.info("Основные обработчики зарегистрированы")
        
        # Регистрируем диалоги
        register_dialogs(dp)
        logger.info("Диалоги зарегистрированы")
        
        # Настраиваем хранилище состояний для aiogram-dialog
        from aiogram.fsm.storage.redis import RedisStorage
        
        storage = RedisStorage(redis_client)
        dp.storage = storage
        logger.info("Хранилище состояний настроено")
        
        logger.info("🚀 Запуск бота...")
        
        # Запускаем бота
        try:
            await dp.start_polling(bot)
        finally:
            # Закрываем соединения
            await database.close()
            await redis_manager.close()
            logger.info("Соединения закрыты")
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)