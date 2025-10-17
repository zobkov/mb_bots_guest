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
    """Получить данные о всех мероприятиях с проверкой лимитов."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    # Получаем все мероприятия
    all_events = await event_service.get_all_events()
    
    # Получаем текущие регистрации пользователя для первичного заполнения
    telegram_id = dialog_manager.event.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    # Если состояние диалога пустое, заполняем текущими регистрациями
    if "selected_optional" not in dialog_manager.dialog_data:
        current_selections = []
        if user:
            registrations = await event_service.get_user_registrations(user.id)
            current_selections = [str(reg.event.id) for reg in registrations]
        dialog_manager.dialog_data["selected_optional"] = current_selections
    
    # Используем выбор из состояния диалога (не из БД!)
    current_selections = dialog_manager.dialog_data.get("selected_optional", [])
    
    # Формируем текст со списком мероприятий
    events_info_lines = []
    
    # Разделяем мероприятия на доступные и заполненные
    available_events = []
    full_events_selected = []
    
    for event in all_events:
        # Получаем количество зарегистрированных
        registered_count = await event_service.get_registered_count(event.id)
        is_full = event.max_participants and registered_count >= event.max_participants
        is_selected = str(event.id) in current_selections
        
        # Для заполненных мероприятий проверяем, выбран ли он сейчас в диалоге
        # Если пользователь уже был зарегистрирован, то он может отменить даже заполненное
        current_db_registrations = []
        if user:
            db_registrations = await event_service.get_user_registrations(user.id)
            current_db_registrations = [str(reg.event.id) for reg in db_registrations]
        
        was_registered_in_db = str(event.id) in current_db_registrations
        
        # Формируем информацию о мероприятии
        if event.max_participants:
            available_spots = event.max_participants - registered_count
            spots_text = f"Осталось мест: {available_spots}" if available_spots > 0 else "🔒 Мест нет"
        else:
            spots_text = "Осталось мест: неограниченно"
        
        # Добавляем описание мероприятия
        description = getattr(event, 'description', None) or ""
        if description != "":
            description = "- " + description
        
        event_info = f"— <b>{event.name}</b> <i>{description}</i>\n📅 {event.day} \t{event.start_time} - {event.end_time}: \n<i>{spots_text}</i>"
        events_info_lines.append(event_info)
        
        event_info_dict = {
            "event": event,
            "is_selected": is_selected,
            "is_full": is_full,
            "registered_count": registered_count,
            "checkbox_text": f"{'☑️' if is_selected else '☐'} {event.day} {event.start_time}-{event.end_time} {event.name}",
        }
        
        # Проверяем, можно ли взаимодействовать с мероприятием
        if is_full and not is_selected and not was_registered_in_db:
            # Заполненное, не выбрано и не было зарегистрировано - недоступно
            event_info_dict["checkbox_text"] = f"🔒 {event.day} {event.start_time}-{event.end_time} {event.name} (заполнено)"
            continue  # Не добавляем в доступные
        elif is_selected and is_full:
            # Заполненное, но выбрано - можно отменить
            full_events_selected.append(event_info_dict)
            continue
        
        # Доступные для взаимодействия
        available_events.append(event_info_dict)
    
    # Объединяем информацию о мероприятиях
    events_info_text = "\n\n".join(events_info_lines)
    
    # Логируем для отладки
    print(f"DEBUG: current_selections (from dialog) = {current_selections}")
    print(f"DEBUG: available_events = {len(available_events)}, full_events_selected = {len(full_events_selected)}")
    
    return {
        "all_events": all_events,
        "available_events": available_events,
        "full_events_selected": full_events_selected,
        "current_selections": current_selections,
        "events_info_text": events_info_text,
    }


async def get_confirmation_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получить данные для подтверждения планируемых изменений."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    
    # Получаем планируемый выбор из состояния диалога
    desired_selections = dialog_manager.dialog_data.get("selected_optional", [])
    
    selected_events = []
    
    # Получаем объекты мероприятий по ID
    for event_id_str in desired_selections:
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
            f"✅ <b>{event.name}</b>\n   📅 {event.day} {event.start_time} — {event.end_time}"
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
            f"✅ <b>{reg.event.name}</b>\n📅 {reg.event.day}    {reg.event.start_time} — {reg.event.end_time}"
            for reg in registrations
        ])
        has_registrations = True
    
    return {
        "registrations": registrations,
        "registrations_text": registrations_text,
        "has_registrations": has_registrations,
        "not_has_registrations": not has_registrations,
    }