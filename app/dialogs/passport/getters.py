"""Геттеры для диалога паспортных данных."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

from aiogram_dialog import DialogManager

from app.services.user_service import UserService
from app.services.passport_service import PassportService


async def _fetch_user_and_passport(
    dialog_manager: DialogManager,
) -> Tuple[Any | None, Any | None]:
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    passport_service: PassportService = dialog_manager.middleware_data["passport_service"]

    telegram_id = dialog_manager.event.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)

    if not user:
        return None, None

    passport_data = await passport_service.get_user_passport_data(user.id)
    return user, passport_data


def _format_passport_overview(passport_data) -> str:
    if not passport_data:
        return (
            "🛂 <b>Данные для оформления пропуска</b>\n\n"
            "Мы ещё не получили твои паспортные данные.\n\n"
            "Нажми «Заполнить», чтобы отправить ФИО, данные паспорта и номер авто (если потребуется парковка)."
        )

    car_number = passport_data.car_number or "—"
    updated_at = passport_data.updated_at
    if isinstance(updated_at, datetime):
        updated_text = updated_at.strftime("%d.%m.%Y %H:%M")
    else:
        updated_text = "—"

    return (
        "🛂 <b>Твои данные для пропуска</b>\n\n"
        f"👤 <b>ФИО:</b> {passport_data.full_name}\n"
        f"🪪 <b>Паспорт:</b> {passport_data.passport_number}\n"
        f"🚗 <b>Авто:</b> {car_number}\n"
        f"🕒 Обновлено: {updated_text}\n\n"
        "Нажми «Заполнить», если нужно внести изменения."
    )


async def get_passport_overview(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Подготовить данные для стартового окна диалога."""
    user, passport_data = await _fetch_user_and_passport(dialog_manager)

    if user is None:
        return {
            "passport_overview_text": (
                "🛂 <b>Данные для оформления пропуска</b>\n\n"
                "Сначала заполни анкету участника, а затем вернись сюда, чтобы указать паспорт."
            ),
            "has_passport_data": False,
            "no_passport_data": True,
            "can_edit_passport": False,
        }

    has_passport = passport_data is not None
    return {
        "passport_overview_text": _format_passport_overview(passport_data),
        "has_passport_data": has_passport,
        "no_passport_data": not has_passport,
        "can_edit_passport": user is not None,
    }


async def get_passport_form_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Данные для окон ввода паспортной информации."""
    user, passport_data = await _fetch_user_and_passport(dialog_manager)

    form_state = dialog_manager.dialog_data.get("passport_form", {})

    full_name = (form_state.get("full_name") or (passport_data.full_name if passport_data else ""))
    passport_number = form_state.get("passport_number") or (
        passport_data.passport_number if passport_data else ""
    )
    car_number = form_state.get("car_number") or (passport_data.car_number if passport_data else "")

    full_name = full_name.strip() if isinstance(full_name, str) else full_name
    passport_number = passport_number.strip() if isinstance(passport_number, str) else passport_number
    if isinstance(car_number, str):
        car_number = car_number.strip()

    return {
        "prefill_full_name": full_name,
        "prefill_passport_number": passport_number,
        "prefill_car_number": car_number,
        "has_passport_data": passport_data is not None,
        "no_passport_data": passport_data is None,
        "passport_overview_text": _format_passport_overview(passport_data),
        "can_edit_passport": user is not None,
    }
