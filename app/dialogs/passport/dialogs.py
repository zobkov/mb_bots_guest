"""Диалог для сбора паспортных данных."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format

from .getters import get_passport_overview, get_passport_form_data
from .handlers import (
    on_start_passport_entry,
    on_cancel_passport_entry,
    on_legacy_passport_continue,
    on_full_name_entered,
    on_passport_number_entered,
    on_car_number_entered,
    on_skip_car_number,
    on_passport_back_to_menu,
)
from ...states import PassportSG


def create_passport_dialog() -> Dialog:
    """Создать диалог для ввода паспортных данных."""
    return Dialog(
        Window(
            Format("{passport_overview_text}"),
            Button(
                Const("✍️ Заполнить или обновить"),
                id="passport_start",
                on_click=on_start_passport_entry,
                when="can_edit_passport",
            ),
            Button(
                Const("🔙 Назад"),
                id="passport_to_menu",
                on_click=on_passport_back_to_menu,
            ),
            getter=get_passport_overview,
            state=PassportSG.instructions,
        ),
        Window(
            Const(
                "ℹ️ <b>Форма обновлена</b>\n\n"
                "Мы немного изменили шаги заполнения паспортных данных."
                " Нажми «Заполнить заново», чтобы продолжить."
            ),
            Format(
                "\nТекущие данные: <b>{prefill_full_name}</b>, {prefill_passport_number}",
                when="prefill_full_name",
            ),
            Button(
                Const("✍️ Заполнить заново"),
                id="legacy_passport_continue",
                on_click=on_legacy_passport_continue,
            ),
            Button(
                Const("🔙 Отмена"),
                id="legacy_passport_cancel",
                on_click=on_cancel_passport_entry,
            ),
            getter=get_passport_form_data,
            state=PassportSG.passport_info,
        ),
        Window(
            Const(
                "✍️ <b>Введи полное ФИО</b>\n\n"
                "Пожалуйста, укажи фамилию, имя и при наличии отчество."
            ),
            Format(
                "\nТекущие данные: <b>{prefill_full_name}</b>",
                when="prefill_full_name",
            ),
            TextInput(
                id="passport_full_name_input",
                on_success=on_full_name_entered,
            ),
            Button(
                Const("🔙 Отмена"),
                id="passport_cancel",
                on_click=on_cancel_passport_entry,
            ),
            getter=get_passport_form_data,
            state=PassportSG.full_name,
        ),
        Window(
            Const(
                "🪪 <b>Серия и номер паспорта</b>\n\n"
                "Введи 10 цифр подряд, можно с пробелом между серией и номером."
            ),
            Format(
                "\nТекущие данные: <b>{prefill_passport_number}</b>",
                when="prefill_passport_number",
            ),
            TextInput(
                id="passport_number_input",
                on_success=on_passport_number_entered,
            ),
            Button(
                Const("🔙 Отмена"),
                id="passport_cancel_from_number",
                on_click=on_cancel_passport_entry,
            ),
            getter=get_passport_form_data,
            state=PassportSG.passport_number,
        ),
        Window(
            Const(
                "🚗 <b>Номер автомобиля</b>\n\n"
                "Если планируешь приезжать на машине, укажи номер.\n"
                "Иначе нажми «Пропустить»."
            ),
            Format(
                "\nТекущий номер: <b>{prefill_car_number}</b>",
                when="prefill_car_number",
            ),
            TextInput(
                id="car_number_input",
                on_success=on_car_number_entered,
            ),
            Row(
                Button(
                    Const("⏭️ Пропустить"),
                    id="skip_car_number",
                    on_click=on_skip_car_number,
                ),
                Button(
                    Const("🔙 Отмена"),
                    id="passport_cancel_from_car",
                    on_click=on_cancel_passport_entry,
                ),
            ),
            getter=get_passport_form_data,
            state=PassportSG.car_number,
        ),
    )
