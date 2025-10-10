"""Скрипт для добавления тестовых мероприятий в базу данных."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config.config import load_config
from app.database.models.registration import Event


async def add_events():
    """Добавить тестовые мероприятия."""
    config = load_config()
    
    # Создаем движок
    engine = create_async_engine(config.database.async_url)
    
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Мероприятия для добавления
    events_data = [
        {
            "name": "Центральная пленарная сессия «Как создать экономику будущего через региональные хабы»",
            "description": "Центральная пленарная сессия конференции",
            "day": "23 октября",
            "start_time": "11:00",
            "end_time": "12:40",
            "event_type": "plenary",
            "is_exclusive": False,
            "max_participants": None,
            "sheet_name": "plenary_session"
        },
        {
            "name": "Выступление Андрея Костина, президента-председателя правления ВТБ",
            "description": "Специальное выступление президента-председателя правления ВТБ",
            "day": "23 октября",
            "start_time": "17:30",
            "end_time": "18:50",
            "event_type": "speech",
            "is_exclusive": False,
            "max_participants": None,
            "sheet_name": "vtb_speech"
        },
        {
            "name": "Кадры для будущего: как стать желанным кандидатом?",
            "description": "Воркшоп о развитии карьеры и профессиональных навыков",
            "day": "23 октября",
            "start_time": "13:10",
            "end_time": "14:30",
            "event_type": "workshop",
            "is_exclusive": True,
            "max_participants": 100,
            "sheet_name": "career_workshop"
        },
        {
            "name": "Возрождение малых городов — новые центры притяжения",
            "description": "Обсуждение развития малых городов и региональной экономики",
            "day": "23 октября",
            "start_time": "13:10",
            "end_time": "14:30",
            "event_type": "workshop",
            "is_exclusive": True,
            "max_participants": 80,
            "sheet_name": "small_cities_workshop"
        },
        {
            "name": "Нейроны мегаполисов: AI, IoT и BigData как цифровая нервная система",
            "description": "Технологический воркшоп о цифровизации городов",
            "day": "24 октября",
            "start_time": "13:10",
            "end_time": "14:30",
            "event_type": "workshop",
            "is_exclusive": True,
            "max_participants": 120,
            "sheet_name": "tech_workshop"
        }
    ]
    
    try:
        async with session_factory() as session:
            # Проверяем, есть ли уже мероприятия
            from sqlalchemy import text
            existing_events = await session.execute(text("SELECT COUNT(*) FROM events"))
            count = existing_events.scalar()
            
            if count > 0:
                print(f"⚠️  В базе уже есть {count} мероприятий. Пропускаем добавление.")
                return
            
            # Добавляем мероприятия
            for event_data in events_data:
                event = Event(**event_data)
                session.add(event)
            
            await session.commit()
            print(f"✅ Добавлено {len(events_data)} мероприятий!")
            
            # Показываем добавленные мероприятия
            print("\n📅 Добавленные мероприятия:")
            for event_data in events_data:
                exclusive_mark = " (взаимоисключающее)" if event_data["is_exclusive"] else ""
                max_part = f" (макс. {event_data['max_participants']})" if event_data["max_participants"] else ""
                print(f"• {event_data['day']} {event_data['start_time']}-{event_data['end_time']}: {event_data['name']}{exclusive_mark}{max_part}")
                
    except Exception as e:
        print(f"❌ Ошибка добавления мероприятий: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_events())