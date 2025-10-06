#!/usr/bin/env python3
"""Скрипт для удаления пользователя и его регистраций."""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.config.config import load_config
from app.database.database import Database
from app.database.models.user import User
from app.database.models.registration import EventRegistration
from sqlalchemy import select, delete


async def delete_user_data(telegram_id: int):
    """Удалить все данные пользователя."""
    config = load_config()
    database = Database(config.database)
    
    try:
        async with database.get_session() as session:
            # Найдем пользователя
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ Пользователь с telegram_id={telegram_id} не найден")
                return
            
            print(f"🔍 Найден пользователь: {user.first_name} {user.last_name} ({user.email})")
            
            # Удаляем регистрации
            registrations_stmt = delete(EventRegistration).where(EventRegistration.user_id == user.id)
            reg_result = await session.execute(registrations_stmt)
            print(f"🗑️ Удалено регистраций: {reg_result.rowcount}")
            
            # Удаляем пользователя
            user_stmt = delete(User).where(User.id == user.id)
            user_result = await session.execute(user_stmt)
            print(f"🗑️ Удален пользователь: {user_result.rowcount}")
            
            await session.commit()
            print("✅ Данные пользователя успешно удалены")
            
    except Exception as e:
        print(f"❌ Ошибка при удалении: {e}")
    finally:
        await database.close()


if __name__ == "__main__":
    user_id = 257026813
    print(f"🗑️ Удаление данных пользователя {user_id}...")
    asyncio.run(delete_user_data(user_id))