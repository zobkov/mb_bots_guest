"""Сервис для работы с мероприятиями и регистрациями."""
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.registration import Event, EventRegistration
from app.database.models.user import User
from app.database.repositories.event_repository import EventRepository, RegistrationRepository
from app.infrastructure.google_sheets.sheets_manager import GoogleSheetsManager


class EventService:
    """Сервис для работы с мероприятиями и регистрациями."""
    
    def __init__(self, session: AsyncSession, sheets_manager: GoogleSheetsManager):
        self.event_repository = EventRepository(session)
        self.registration_repository = RegistrationRepository(session)
        self.sheets_manager = sheets_manager
    
    async def get_all_events(self) -> List[Event]:
        """Получить все мероприятия."""
        return await self.event_repository.get_all_events()
    
    async def get_user_registrations(self, user_id: int) -> List[EventRegistration]:
        """Получить регистрации пользователя."""
        return await self.registration_repository.get_user_registrations(user_id)
    
    async def can_register_for_event(self, user_id: int, event_id: int) -> Tuple[bool, str]:
        """
        Проверить, может ли пользователь зарегистрироваться на мероприятие.
        Возвращает (можно_ли_регистрироваться, причина_если_нельзя)
        """
        # Проверяем, не зарегистрирован ли уже
        if await self.registration_repository.is_user_registered(user_id, event_id):
            return False, "Вы уже зарегистрированы на это мероприятие"
        
        # Получаем мероприятие
        event = await self.event_repository.get_by_id(event_id)
        if not event:
            return False, "Мероприятие не найдено"
        
        # Проверяем взаимоисключающие мероприятия
        if event.is_exclusive:
            if await self.registration_repository.has_exclusive_registration(user_id):
                return False, "Вы уже зарегистрированы на одно из взаимоисключающих мероприятий этого времени"
        
        # Проверяем лимит участников
        if event.max_participants:
            current_count = await self.registration_repository.get_event_participants_count(event_id)
            if current_count >= event.max_participants:
                return False, "Достигнуто максимальное количество участников"
        
        return True, ""
    
    async def register_user_for_event(self, user: User, event_id: int) -> Tuple[bool, str]:
        """
        Зарегистрировать пользователя на мероприятие.
        Возвращает (успешно_ли, сообщение)
        """
        can_register, reason = await self.can_register_for_event(user.id, event_id)
        if not can_register:
            return False, reason
        
        try:
            # Регистрируем в базе данных
            registration = await self.registration_repository.register_user(user.id, event_id)
            
            # Получаем мероприятие для добавления в Google Sheets
            event = await self.event_repository.get_by_id(event_id)
            if event:
                # Добавляем в Google Sheets
                await self.sheets_manager.add_user_to_event_sheet(
                    user=user,
                    event_name=event.name,
                    sheet_name=event.sheet_name
                )
            
            return True, f"Вы успешно зарегистрированы на мероприятие: {event.name}"
            
        except Exception as e:
            return False, f"Ошибка при регистрации: {str(e)}"
    
    async def unregister_user_from_event(self, user: User, event_id: int) -> Tuple[bool, str]:
        """
        Отменить регистрацию пользователя на мероприятие.
        Возвращает (успешно_ли, сообщение)
        """
        if not await self.registration_repository.is_user_registered(user.id, event_id):
            return False, "Вы не зарегистрированы на это мероприятие"
        
        try:
            # Получаем мероприятие
            event = await self.event_repository.get_by_id(event_id)
            
            # Отменяем регистрацию в базе данных
            success = await self.registration_repository.unregister_user(user.id, event_id)
            
            if success and event:
                # Удаляем из Google Sheets
                await self.sheets_manager.remove_user_from_event_sheet(
                    user=user,
                    sheet_name=event.sheet_name
                )
                return True, f"Регистрация на мероприятие '{event.name}' отменена"
            else:
                return False, "Ошибка при отмене регистрации"
                
        except Exception as e:
            return False, f"Ошибка при отмене регистрации: {str(e)}"
    
    async def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Получить мероприятие по ID."""
        return await self.event_repository.get_by_id(event_id)