"""Скрипт для проверки подключений к инфраструктуре."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from app.config.config import load_config
from app.database.database import Database
from app.infrastructure.redis.redis_manager import RedisManager
from app.infrastructure.google_sheets.sheets_manager import GoogleSheetsManager


async def check_database():
    """Проверить подключение к базе данных."""
    print("🔍 Проверка подключения к PostgreSQL...")
    database = None
    try:
        config = load_config()
        database = Database(config.database)
        
        # Правильный способ работы с async generator
        session_gen = database.get_session()
        session = await session_gen.__anext__()
        
        try:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ PostgreSQL: подключение успешно")
                return True
            else:
                print("❌ PostgreSQL: ошибка выполнения запроса")
                return False
        finally:
            await session.close()
                
    except Exception as e:
        print(f"❌ PostgreSQL: ошибка подключения - {e}")
        return False
    finally:
        if database:
            await database.close()


async def check_redis():
    """Проверить подключение к Redis."""
    print("🔍 Проверка подключения к Redis...")
    try:
        config = load_config()
        redis_manager = RedisManager(config.redis)
        
        redis_client = await redis_manager.get_redis()
        await redis_client.ping()
        print("✅ Redis: подключение успешно")
        return True
        
    except Exception as e:
        print(f"❌ Redis: ошибка подключения - {e}")
        return False
    finally:
        await redis_manager.close()


def check_google_sheets():
    """Проверить подключение к Google Sheets."""
    print("🔍 Проверка подключения к Google Sheets...")
    try:
        config = load_config()
        sheets_manager = GoogleSheetsManager(config.google_sheets)
        
        # Пробуем получить клиент
        client = sheets_manager._get_client()
        print("✅ Google Sheets: аутентификация успешна")
        
        # Пробуем открыть таблицу
        spreadsheet = sheets_manager._get_spreadsheet()
        print(f"✅ Google Sheets: таблица '{spreadsheet.title}' открыта успешно")
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets: ошибка подключения - {e}")
        return False


async def main():
    """Главная функция проверки."""
    print("🚀 Проверка подключений к инфраструктуре...\n")
    
    results = []
    
    # Проверяем базу данных
    db_ok = await check_database()
    results.append(("PostgreSQL", db_ok))
    print()
    
    # Проверяем Redis
    redis_ok = await check_redis()
    results.append(("Redis", redis_ok))
    print()
    
    # Проверяем Google Sheets
    sheets_ok = check_google_sheets()
    results.append(("Google Sheets", sheets_ok))
    print()
    
    # Итоговый отчет
    print("📊 Итоговый отчет:")
    print("=" * 40)
    
    all_ok = True
    for service, status in results:
        status_icon = "✅" if status else "❌"
        status_text = "OK" if status else "ОШИБКА"
        print(f"{status_icon} {service:<15} {status_text}")
        
        if not status:
            all_ok = False
    
    print("=" * 40)
    
    if all_ok:
        print("🎉 Все сервисы работают корректно!")
        print("Можно запускать бота: python main.py")
    else:
        print("⚠️  Есть проблемы с подключениями.")
        print("Проверьте настройки в .env и доступность сервисов.")


if __name__ == "__main__":
    asyncio.run(main())