"""Утилиты для диалога регистрации на мероприятия."""
from typing import List, Set

from app.database.models.registration import Event


def get_conflicting_events(events: List[Event]) -> List[Set[int]]:
    """
    Получить группы взаимоисключающих мероприятий.
    Возвращает список множеств ID мероприятий, которые нельзя выбирать одновременно.
    """
    conflicting_groups = []
    
    # Группируем взаимоисключающие мероприятия по времени
    exclusive_events = [event for event in events if event.is_exclusive]
    
    if exclusive_events:
        # Все взаимоисключающие мероприятия в одной группе
        exclusive_ids = {event.id for event in exclusive_events}
        conflicting_groups.append(exclusive_ids)
    
    return conflicting_groups


def validate_event_selection(
    selected_event_ids: List[int], 
    events: List[Event]
) -> tuple[bool, str]:
    """
    Валидация выбранных мероприятий на предмет конфликтов.
    Возвращает (валидно_ли, сообщение_об_ошибке)
    """
    if not selected_event_ids:
        return False, "Необходимо выбрать хотя бы одно мероприятие"
    
    # Получаем выбранные мероприятия
    selected_events = [event for event in events if event.id in selected_event_ids]
    
    # Проверяем взаимоисключающие мероприятия
    exclusive_selected = [event for event in selected_events if event.is_exclusive]
    
    if len(exclusive_selected) > 1:
        return False, (
            "Вы можете выбрать только одно мероприятие из взаимоисключающих "
            "(13:10 — 14:30), так как они проходят одновременно"
        )
    
    return True, ""


def format_event_for_display(event: Event, is_selected: bool = False) -> str:
    """Форматировать мероприятие для отображения."""
    checkbox = "☑️" if is_selected else "☐"
    
    return f"{checkbox} <b>({event.start_time} — {event.end_time})</b> {event.name}"