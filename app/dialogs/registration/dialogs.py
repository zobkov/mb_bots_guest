"""Диалог регистрации на мероприятия."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Back, Select, Group, Column, Radio, Checkbox, Row

from .handlers import (
    on_exclusive_event_changed,
    on_optional_event_changed,
    on_skip_exclusive,
    on_next_to_optional,
    on_next_to_confirmation,
    on_confirm_final_registration,
    on_edit_registrations,
    on_unregister_event,
    on_back_to_menu,
    on_enter_optional_events
)
from .getters import (
    get_exclusive_events_data,
    get_optional_events_data,
    get_confirmation_data,
    get_my_registrations_data
)
from ...states import RegistrationSG


def create_registration_dialog() -> Dialog:
    """Создать диалог регистрации на мероприятия."""
    return Dialog(
        # Окно выбора взаимоисключающих мероприятий (Radio)
        Window(
            Const(
                "📅 <b>Выберите одно мероприятие из трех</b>\n"
                "<i>(они проходят одновременно, поэтому можно попасть только на одно)</i>\n"
                "• (13:10 — 14:30) Кадры для будущего: как стать желанным кандидатом?\n"
                "• (13:10 — 14:30) Возрождение малых городов — новые центры притяжения\n"
                "• (13:10 — 14:30) Нейроны мегаполисов: AI, IoT и BigData как цифровая нервная система\n"
            ),
            Radio(
                Format("🔘 {item.name}"),
                Format("⚪️ {item.name}"),
                id="exclusive_radio",
                item_id_getter=lambda event: str(event.id),
                items="exclusive_events",
                on_state_changed=on_exclusive_event_changed,
            ),
            Row(
                Button(
                    Const("⏭️ Пропустить"),
                    id="skip_exclusive",
                    on_click=on_skip_exclusive,
                ),
                Button(
                    Const("➡️ Далее"),
                    id="next_to_optional",
                    on_click=on_next_to_optional,
                ),
            ),
            getter=get_exclusive_events_data,
            state=RegistrationSG.exclusive_events,
        ),
        
        # Окно выбора дополнительных мероприятий (Checkbox)
        Window(
            Const(
                "📅 <b>Выберите дополнительные мероприятия</b>\n"
                "<i>(можно выбрать оба, один или ни одного)</i>\n\n"
                "• (11:00 — 12:40) Центральная пленарная сессия\n"
                "«Как создать экономику будущего через региональные хабы»\n\n"
                "• (17:30 — 18:50) Выступление Андрея Костина, президента-председателя правления ВТБ"
            ),
            Checkbox(
                Const("☑️ (11:00 — 12:40) Центральная пленарная сессия"),
                Const("☐ (11:00 — 12:40) Центральная пленарная сессия"),
                id="plenary_checkbox",
                default=False,
                on_state_changed=on_optional_event_changed,
            ),
            Checkbox(
                Const("☑️ (17:30 — 18:50) Выступление Андрея Костина"),
                Const("☐ (17:30 — 18:50) Выступление Андрея Костина"),
                id="vtb_checkbox",
                default=False,
                on_state_changed=on_optional_event_changed,
            ),
            Row(
                Back(Const("⬅️ Назад")),
                Button(
                    Const("➡️ Подтвердить"),
                    id="next_to_confirmation",
                    on_click=on_next_to_confirmation,
                ),
            ),
            getter=get_optional_events_data,
            on_process_result=on_enter_optional_events,
            state=RegistrationSG.optional_events,
        ),
        
        # Окно подтверждения выбора
        Window(
            Const("<b>📋 Подтверждение регистрации</b>\n\n"),
            Format(
                "Вы выбрали следующие мероприятия:\n\n"
                "{events_text}\n\n"
                "Подтвердить регистрацию?",
                when="has_selections"
            ),
            Const(
                "❌ Вы не выбрали ни одного мероприятия.\n"
                "Вернитесь назад и сделайте выбор.",
                when="not_has_selections"
            ),
            Row(
                Back(Const("⬅️ Назад")),
                Button(
                    Const("✅ Подтвердить"),
                    id="confirm_final",
                    on_click=on_confirm_final_registration,
                    when="has_selections"
                ),
            ),
            getter=get_confirmation_data,
            state=RegistrationSG.confirm_registration,
        ),
        
        # Окно с текущими регистрациями
        Window(
            Format(
                "📋 <b>Ваши текущие регистрации:</b>\n\n"
                "{registrations_text}\n\n",
                when="has_registrations"
            ),
            Const(
                "📋 <b>Ваши текущие регистрации:</b>\n\n"
                "У вас пока нет регистраций на мероприятия.\n\n",
                when="not_has_registrations"
            ),
            Group(
                Select(
                    Format("❌ {item.event.name}\n    📅 {item.event.start_time} — {item.event.end_time}"),
                    id="unregister_select",
                    items="registrations",
                    item_id_getter=lambda reg: str(reg.event.id),
                    on_click=on_unregister_event,
                ),
                id="registrations_group",
                width=1,
                when="has_registrations"
            ),
            Column(
                Button(
                    Const("✏️ Изменить регистрации"),
                    id="edit_registrations",
                    on_click=on_edit_registrations,
                ),
                Button(
                    Const("🔙 Назад в меню"),
                    id="back_to_menu",
                    on_click=on_back_to_menu,
                ),
            ),
            getter=get_my_registrations_data,
            state=RegistrationSG.my_registrations,
        ),
    )