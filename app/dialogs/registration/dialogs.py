"""Диалог регистрации на мероприятия."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Back, Select, Group, Column, Row, Cancel

from .handlers import (
    on_toggle_event_registration,
    on_confirm_final_registration,
    on_edit_registrations,
    on_unregister_event,
    on_back_to_menu,
    on_enter_events_list
)
from .getters import (
    get_optional_events_data,
    get_confirmation_data,
    get_my_registrations_data
)
from ...states import RegistrationSG


def create_registration_dialog() -> Dialog:
    """Создать диалог регистрации на мероприятия."""
    return Dialog(
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
            Column(
                Button(
                    Const("✏️ Изменить регистрации"),
                    id="edit_registrations",
                    on_click=on_edit_registrations,
                ),
                Cancel(
                    Const("🔙 Назад"),
                    id="back_to_menu",
                ),
            ),
            getter=get_my_registrations_data,
            state=RegistrationSG.my_registrations,
        ),

        # Главное окно выбора мероприятий
        Window(
            Format(
                "{events_info_text}\n\n"
                "<b>Выбери мероприятия для регистрации (или убери текущий выбор, чтобы отказаться)</b>\n\n"
            ),
            Group(
                Select(
                    Format("{item[checkbox_text]}"),
                    id="available_events",
                    items="available_events",
                    item_id_getter=lambda item: str(item["event"].id),
                    on_click=on_toggle_event_registration,
                ),
                Select(
                    Format("{item[checkbox_text]}"),
                    id="full_events",
                    items="full_events_selected",
                    item_id_getter=lambda item: str(item["event"].id),
                    on_click=on_toggle_event_registration,
                ),
                id="events_group",
                width=1,
            ),
            Row(
                Button(
                    Const("➡️ Подтвердить изменения"),
                    id="next_to_confirmation",
                    on_click=on_confirm_final_registration,
                ),
            ),
            Row(
                Button(
                    Const("🔙 Назад"),
                    id="back_to_menu",
                    on_click=on_back_to_menu,
                ),
            ),
            getter=get_optional_events_data,
            on_process_result=on_enter_events_list,
            state=RegistrationSG.optional_events,
        ),
        

    )