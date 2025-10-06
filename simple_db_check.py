"""Простая проверка подключения к PostgreSQL."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

import psycopg
from app.config.config import load_config


async def simple_db_check():
    """Простая проверка подключения к PostgreSQL."""
    config = load_config()
    
    # Формируем строку подключения для psycopg (синхронная версия)
    connection_string = f"postgresql://{config.database.user}:{config.database.password}@{config.database.host}:{config.database.port}/{config.database.database}"
    
    try:
        print(f"🔍 Попытка подключения к: {config.database.host}:{config.database.port}")
        print(f"📊 База данных: {config.database.database}")
        print(f"👤 Пользователь: {config.database.user}")
        
        # Попробуем синхронное подключение
        with psycopg.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()
                print(f"✅ PostgreSQL подключение успешно!")
                print(f"📋 Версия PostgreSQL: {version[0]}")
                return True
                
    except psycopg.OperationalError as e:
        if "password authentication failed" in str(e):
            print("❌ Ошибка аутентификации: неверный пользователь или пароль")
            print("💡 Проверьте настройки DB_USER и DB_PASS в .env файле")
        elif "does not exist" in str(e):
            print("❌ База данных не существует")
            print("💡 Проверьте настройку DB_NAME в .env файле")
        elif "Connection refused" in str(e):
            print("❌ Не удается подключиться к серверу PostgreSQL")
            print("💡 Проверьте настройки DB_HOST и DB_PORT в .env файле")
        else:
            print(f"❌ Ошибка подключения: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(simple_db_check())
    
    if success:
        print("\n🎉 Подключение к PostgreSQL работает!")
        print("Можете продолжить настройку бота.")
    else:
        print("\n⚠️  Нужно исправить настройки подключения к PostgreSQL.")
        print("Обратитесь к администратору базы данных.")