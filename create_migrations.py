"""Скрипт инициализации и создания миграций для Alembic."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.config import load_config
from app.database.models.base import Base
# Импортируем все модели для создания таблиц
from app.database.models.user import User
from app.database.models.registration import Event, EventRegistration


async def create_migration():
    """Создать автоматическую миграцию."""
    config = load_config()
    
    # Создаем движок
    engine = create_async_engine(config.database.async_url)
    
    try:
        # Создаем все таблицы (для первоначальной настройки)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Таблицы созданы успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
    finally:
        await engine.dispose()


def init_alembic():
    """Инициализировать Alembic."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.init(alembic_cfg, "migrations")
        print("✅ Alembic инициализирован!")
    except Exception as e:
        print(f"❌ Ошибка инициализации Alembic: {e}")


def create_alembic_migration(message: str = "Initial migration"):
    """Создать миграцию Alembic."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.revision(alembic_cfg, autogenerate=True, message=message)
        print(f"✅ Миграция '{message}' создана!")
    except Exception as e:
        print(f"❌ Ошибка создания миграции: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Управление миграциями базы данных")
    parser.add_argument("--init", action="store_true", help="Инициализировать Alembic")
    parser.add_argument("--create", action="store_true", help="Создать таблицы напрямую")
    parser.add_argument("--migration", type=str, help="Создать миграцию с указанным сообщением")
    
    args = parser.parse_args()
    
    if args.init:
        init_alembic()
    elif args.create:
        asyncio.run(create_migration())
    elif args.migration:
        create_alembic_migration(args.migration)
    else:
        print("Используйте --init, --create или --migration 'описание'")