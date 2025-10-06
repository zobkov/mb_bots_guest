"""Диалог регистрации на мероприятия."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Back, Select, Group, Column

from .handlers import (
    on_event_select,
    on_register_confirm,
    on_show_my_registrations,
    on_unregister_event,
    on_back_to_menu
)
from .getters import get_events_data, get_my_registrations_data
from ...states import RegistrationSG


def create_registration_dialog() -> Dialog:
    """Создать диалог регистрации на мероприятия."""
    return Dialog(
        # Окно со списком мероприятий
        Window(
            Const(
                "📅 <b>Сейчас доступна регистрация на следующие мероприятия:</b>\n\n"
                "<i>Оба на выбор:</i>\n\n"
                "☐ <b>(11:00 — 12:40)</b> Центральная пленарная сессия\n"
                "«Как создать экономику будущего через региональные хабы»\n\n"
                "☐ <b>(17:30 — 18:50)</b> Выступление Андрея Костина, президента-председателя правления ВТБ\n\n"
                "⸻\n\n"
                "<i>Одно из трех на выбор:</i>\n"
                "(обрати внимание, что они идут одновременно в разных аудиториях, поэтому попасть можно только на одно)\n\n"
                "○ <b>(13:10 — 14:30)</b> Кадры для будущего: как стать желанным кандидатом?\n"
                "○ <b>(13:10 — 14:30)</b> Возрождение малых городов — новые центры притяжения\n"
                "○ <b>(13:10 — 14:30)</b> Нейроны мегаполисов: AI, IoT и BigData как цифровая нервная система\n\n"
                "Нажмите на мероприятие, чтобы зарегистрироваться:"
            ),
            Group(
                Select(
                    Format("📅 ({item.start_time} — {item.end_time}) {item.name}"),
                    id="event_select",
                    items="events",
                    item_id_getter=lambda event: event.id,
                    on_click=on_event_select,
                ),
                id="events_group",
                width=1,
            ),
            Column(
                Button(
                    Const("📋 Мои регистрации"),
                    id="my_registrations",
                    on_click=on_show_my_registrations,
                ),
                Button(
                    Const("🔙 Назад в меню"),
                    id="back_to_menu",
                    on_click=on_back_to_menu,
                ),
            ),
            getter=get_events_data,
            state=RegistrationSG.events_list,
        ),
        
        # Окно с текущими регистрациями
        Window(
            Format(
                "📋 <b>Ваши текущие регистрации:</b>\n\n"
                "{registrations_text}\n\n"
                "Нажмите на мероприятие, чтобы отменить регистрацию:"
            ),
            Group(
                Select(
                    Format("❌ ({item.event.start_time} — {item.event.end_time}) {item.event.name}"),
                    id="unregister_select",
                    items="registrations",
                    item_id_getter=lambda reg: reg.event.id,
                    on_click=on_unregister_event,
                ),
                id="registrations_group",
                width=1,
            ),
            Back(Const("🔙 Назад к списку мероприятий")),
            getter=get_my_registrations_data,
            state=RegistrationSG.my_registrations,
        ),
    )