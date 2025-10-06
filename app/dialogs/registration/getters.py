"""Геттеры для диалога регистрации на мероприятия."""
from typing import Dict, Any, List

from aiogram_dialog import DialogManager

from app.services.event_service import EventService
from app.services.user_service import UserService


async def get_events_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получить данные о мероприятиях."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    
    # Получаем все мероприятия
    events = await event_service.get_all_events()
    
    # Получаем текущие выбранные мероприятия из состояния диалога
    selected_events = dialog_manager.dialog_data.get("selected_events", [])
    
    return {
        "events": events,
        "selected_events": selected_events,
    }


async def get_my_registrations_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получить данные о регистрациях пользователя."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    telegram_id = dialog_manager.event.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if not user:
        return {
            "registrations": [],
            "registrations_text": "У вас пока нет регистраций на мероприятия."
        }
    
    registrations = await event_service.get_user_registrations(user.id)
    
    if not registrations:
        registrations_text = "У вас пока нет регистраций на мероприятия."
    else:
        registrations_text = "\n".join([
            f"✅ <b>{reg.event.name}</b>\n   📅 {reg.event.start_time} — {reg.event.end_time}"
            for reg in registrations
        ])
    
    return {
        "registrations": registrations,
        "registrations_text": registrations_text,
    }