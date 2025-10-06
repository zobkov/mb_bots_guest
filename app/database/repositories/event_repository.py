"""Репозиторий для работы с мероприятиями и регистрациями."""
from typing import List, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.registration import Event, EventRegistration
from app.database.models.user import User


class EventRepository:
    """Репозиторий для работы с мероприятиями."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_events(self) -> List[Event]:
        """Получить все мероприятия."""
        stmt = select(Event).order_by(Event.start_time)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_id(self, event_id: int) -> Optional[Event]:
        """Получить мероприятие по ID."""
        stmt = select(Event).where(Event.id == event_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_exclusive_events(self) -> List[Event]:
        """Получить взаимоисключающие мероприятия."""
        stmt = select(Event).where(Event.is_exclusive == True).order_by(Event.start_time)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class RegistrationRepository:
    """Репозиторий для работы с регистрациями."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_registrations(self, user_id: int) -> List[EventRegistration]:
        """Получить все регистрации пользователя."""
        stmt = (
            select(EventRegistration)
            .options(selectinload(EventRegistration.event))
            .where(EventRegistration.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def is_user_registered(self, user_id: int, event_id: int) -> bool:
        """Проверить, зарегистрирован ли пользователь на мероприятие."""
        stmt = select(EventRegistration).where(
            and_(
                EventRegistration.user_id == user_id,
                EventRegistration.event_id == event_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def register_user(self, user_id: int, event_id: int) -> EventRegistration:
        """Зарегистрировать пользователя на мероприятие."""
        registration = EventRegistration(
            user_id=user_id,
            event_id=event_id
        )
        self.session.add(registration)
        await self.session.flush()
        return registration
    
    async def unregister_user(self, user_id: int, event_id: int) -> bool:
        """Отменить регистрацию пользователя на мероприятие."""
        stmt = select(EventRegistration).where(
            and_(
                EventRegistration.user_id == user_id,
                EventRegistration.event_id == event_id
            )
        )
        result = await self.session.execute(stmt)
        registration = result.scalar_one_or_none()
        
        if registration:
            await self.session.delete(registration)
            await self.session.flush()
            return True
        return False
    
    async def has_exclusive_registration(self, user_id: int) -> bool:
        """Проверить, есть ли у пользователя регистрация на взаимоисключающее мероприятие."""
        stmt = (
            select(EventRegistration)
            .join(Event)
            .where(
                and_(
                    EventRegistration.user_id == user_id,
                    Event.is_exclusive == True
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_event_participants_count(self, event_id: int) -> int:
        """Получить количество участников мероприятия."""
        stmt = select(func.count(EventRegistration.id)).where(
            EventRegistration.event_id == event_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0