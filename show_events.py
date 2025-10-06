#!/usr/bin/env python3
"""Скрипт для просмотра мероприятий."""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.config.config import load_config
from app.database.database import Database
from app.database.models.registration import Event
from sqlalchemy import select


async def show_events():
    """Показать все мероприятия."""
    config = load_config()
    database = Database(config.database)
    
    try:
        async with database.get_session() as session:
            stmt = select(Event).order_by(Event.start_time)
            result = await session.execute(stmt)
            events = result.scalars().all()
            
            print("📅 Мероприятия в базе данных:")
            print("=" * 50)
            for event in events:
                print(f"ID: {event.id}")
                print(f"Название: {event.name}")
                print(f"Время: {event.start_time} — {event.end_time}")
                print(f"Взаимоисключающее: {event.is_exclusive}")
                print(f"Слаг: {event.slug}")
                print("-" * 30)
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(show_events())