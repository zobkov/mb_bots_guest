"""Геттеры для диалога регистрации на мероприятия."""
from typing import Dict, Any, List

from aiogram_dialog import DialogManager

from app.services.event_service import EventService
from app.services.user_service import UserService


async def get_exclusive_events_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получить данные о взаимоисключающих мероприятиях (Radio)."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    # Получаем все мероприятия
    all_events = await event_service.get_all_events()
    
    # Фильтруем взаимоисключающие мероприятия
    exclusive_events = [event for event in all_events if event.is_exclusive]
    
    # Получаем текущие регистрации пользователя для предзаполнения
    telegram_id = dialog_manager.event.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    current_exclusive_selection = None
    if user:
        registrations = await event_service.get_user_registrations(user.id)
        for reg in registrations:
            if reg.event.is_exclusive:
                current_exclusive_selection = str(reg.event.id)
                break
    
    # Если есть сохраненный выбор из состояния диалога, используем его
    if "selected_exclusive" in dialog_manager.dialog_data:
        current_exclusive_selection = dialog_manager.dialog_data["selected_exclusive"]
    
    # Устанавливаем выбранный элемент в Radio
    if current_exclusive_selection:
        try:
            radio_widget = dialog_manager.find("exclusive_radio")
            if radio_widget:
                await radio_widget.set_checked(current_exclusive_selection)
        except:
            pass
    
    return {
        "exclusive_events": exclusive_events,
        "current_exclusive_selection": current_exclusive_selection,
    }


async def get_optional_events_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получить данные о дополнительных мероприятиях (Checkbox)."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    # Получаем все мероприятия
    all_events = await event_service.get_all_events()
    
    # Фильтруем дополнительные мероприятия (не взаимоисключающие)
    optional_events = [event for event in all_events if not event.is_exclusive]
    
    # Получаем текущие регистрации пользователя для предзаполнения
    telegram_id = dialog_manager.event.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    current_optional_selections = []
    if user:
        registrations = await event_service.get_user_registrations(user.id)
        for reg in registrations:
            if not reg.event.is_exclusive:
                current_optional_selections.append(str(reg.event.id))
    
    # Если есть сохраненный выбор из состояния диалога, используем его
    if "selected_optional" in dialog_manager.dialog_data:
        current_optional_selections = dialog_manager.dialog_data["selected_optional"]
    
    # Устанавливаем состояние чекбоксов
    plenary_checked = False
    vtb_checked = False
    
    for event in optional_events:
        if str(event.id) in current_optional_selections:
            if event.sheet_name == "plenary_session":
                plenary_checked = True
            elif event.sheet_name == "vtb_speech":
                vtb_checked = True
    
    # Логируем для отладки
    print(f"DEBUG: current_optional_selections = {current_optional_selections}")
    print(f"DEBUG: plenary_checked = {plenary_checked}, vtb_checked = {vtb_checked}")
    
    return {
        "optional_events": optional_events,
        "current_optional_selections": current_optional_selections,
        "plenary_checked": plenary_checked,
        "vtb_checked": vtb_checked,
    }


async def get_confirmation_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получить данные для подтверждения регистрации."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    
    # Получаем выбранные мероприятия из состояния диалога
    selected_exclusive = dialog_manager.dialog_data.get("selected_exclusive")
    selected_optional = dialog_manager.dialog_data.get("selected_optional", [])
    
    selected_events = []
    
    # Добавляем выбранное взаимоисключающее мероприятие
    if selected_exclusive:
        try:
            event_id = int(selected_exclusive)
            event = await event_service.get_event_by_id(event_id)
            if event:
                selected_events.append(event)
        except (ValueError, TypeError):
            pass
    
    # Добавляем выбранные дополнительные мероприятия
    for event_id_str in selected_optional:
        try:
            event_id = int(event_id_str)
            event = await event_service.get_event_by_id(event_id)
            if event:
                selected_events.append(event)
        except (ValueError, TypeError):
            pass
    
    # Формируем текст для отображения
    if selected_events:
        events_text = "\n".join([
            f"✅ <b>{event.name}</b>\n   📅 {event.start_time} — {event.end_time}"
            for event in selected_events
        ])
    else:
        events_text = "❌ Мероприятия не выбраны"
    
    return {
        "selected_events": selected_events,
        "events_text": events_text,
        "has_selections": len(selected_events) > 0,
        "not_has_selections": len(selected_events) == 0,
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
            "registrations_text": "У вас пока нет регистраций на мероприятия.",
            "has_registrations": False,
        }
    
    registrations = await event_service.get_user_registrations(user.id)
    
    if not registrations:
        registrations_text = "У вас пока нет регистраций на мероприятия."
        has_registrations = False
    else:
        registrations_text = "\n\n".join([
            f"✅ <b>{reg.event.name}</b>\n   📅 {reg.event.start_time} — {reg.event.end_time}"
            for reg in registrations
        ])
        has_registrations = True
    
    return {
        "registrations": registrations,
        "registrations_text": registrations_text,
        "has_registrations": has_registrations,
        "not_has_registrations": not has_registrations,
    }