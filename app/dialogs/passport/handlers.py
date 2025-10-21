"""Обработчики для диалога паспортных данных."""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from app.services.passport_service import PassportService
from app.services.user_service import UserService
from app.states import MainMenuSG, PassportSG


def _normalize_full_name(raw_text: str) -> Optional[str]:
    """Преобразовать ввод пользователя в корректное ФИО."""
    normalized = " ".join(part.strip() for part in raw_text.replace("\n", " ").split() if part.strip())
    if not normalized:
        return None

    tokens = normalized.split()
    # Требуем минимум имя и фамилию
    if len(tokens) < 2:
        return None

    # Фильтруем явные цифры внутри имени
    if any(any(char.isdigit() for char in token) for token in tokens):
        return None

    return " ".join(tokens)


def _normalize_passport_number(raw_text: str) -> Optional[str]:
    """Нормализовать серию и номер паспорта (10 цифр)."""
    digits = re.sub(r"\D", "", raw_text)
    if len(digits) != 10:
        return None

    return f"{digits[:4]} {digits[4:]}"


async def _load_user(dialog_manager: DialogManager, telegram_id: int):
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    return await user_service.get_user_by_telegram_id(telegram_id)


async def _prepare_passport_form(dialog_manager: DialogManager, user) -> None:
    """Заполнить данные формы из БД для пользователя."""
    passport_service: PassportService = dialog_manager.middleware_data["passport_service"]
    passport_data = await passport_service.get_user_passport_data(user.id)

    dialog_manager.dialog_data["passport_form"] = {
        "full_name": passport_data.full_name if passport_data else "",
        "passport_number": passport_data.passport_number if passport_data else "",
        "car_number": passport_data.car_number if passport_data else "",
    }


async def _save_passport_data(
    dialog_manager: DialogManager,
    telegram_id: int,
    event_sender: Message | CallbackQuery,
) -> None:
    passport_service: PassportService = dialog_manager.middleware_data["passport_service"]
    user = await _load_user(dialog_manager, telegram_id)
    if not user:
        if isinstance(event_sender, CallbackQuery):
            await event_sender.answer("Сначала пройдите регистрацию.", show_alert=True)
        else:
            await event_sender.answer("❌ Сначала пройди регистрацию через главное меню.")
        await dialog_manager.switch_to(PassportSG.instructions)
        return

    form_state: Dict[str, Any] = dialog_manager.dialog_data.get("passport_form", {})
    full_name = form_state.get("full_name")
    passport_number = form_state.get("passport_number")
    car_number = form_state.get("car_number")

    if not full_name or not passport_number:
        if isinstance(event_sender, CallbackQuery):
            await event_sender.answer("Заполни ФИО и паспорт.", show_alert=True)
        else:
            await event_sender.answer("❌ Нужно указать ФИО и паспортные данные.")
        return

    try:
        await passport_service.upsert_user_passport_data(
            user=user,
            full_name=full_name,
            passport_number=passport_number,
            car_number=car_number,
        )
    except Exception as exc:  # pragma: no cover - защитный путь
        error_text = "❌ Не удалось сохранить данные. Попробуй позже."
        if isinstance(event_sender, CallbackQuery):
            await event_sender.answer(error_text, show_alert=True)
            if event_sender.message:
                await event_sender.message.answer(error_text)
        else:
            await event_sender.answer(error_text)

        logger = dialog_manager.middleware_data.get("logger")
        if logger:
            logger.error("Ошибка при сохранении паспортных данных: %s", exc)
        return

    success_text = (
        "✅ Паспортные данные сохранены. "
        "Мы обновили информацию для оформления пропуска."
    )

    if isinstance(event_sender, CallbackQuery):
        await event_sender.answer("Данные сохранены", show_alert=False)
        await event_sender.message.answer(success_text)
    else:
        await event_sender.answer(success_text)

    dialog_manager.dialog_data.pop("passport_form", None)
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.switch_to(PassportSG.instructions)


async def on_start_passport_entry(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Перейти к вводу паспортных данных."""
    user = await _load_user(dialog_manager, callback.from_user.id)
    if not user:
        await callback.answer("Сначала пройдите регистрацию.", show_alert=True)
        return

    await _prepare_passport_form(dialog_manager, user)

    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.switch_to(PassportSG.full_name)


async def on_legacy_passport_continue(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Перенаправить пользователей со старого состояния на новую форму."""
    user = await _load_user(dialog_manager, callback.from_user.id)
    if not user:
        await callback.answer("Сначала пройдите регистрацию.", show_alert=True)
        await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)
        return

    await _prepare_passport_form(dialog_manager, user)

    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.switch_to(PassportSG.full_name)


async def on_cancel_passport_entry(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Вернуться к стартовому окну без сохранения."""
    dialog_manager.dialog_data.pop("passport_form", None)
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.switch_to(PassportSG.instructions)


async def on_full_name_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработать ввод полного ФИО."""
    full_name = _normalize_full_name(text)
    if not full_name:
        await message.answer(
            "❌ Укажи фамилию и имя полностью. Допускается отчество, но без цифр."
        )
        return

    dialog_manager.dialog_data.setdefault("passport_form", {})
    dialog_manager.dialog_data["passport_form"]["full_name"] = full_name

    await dialog_manager.switch_to(PassportSG.passport_number)


async def on_passport_number_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработать ввод серии и номера паспорта."""
    passport_number = _normalize_passport_number(text)
    if not passport_number:
        await message.answer(
            "❌ Нужно указать серию и номер паспорта (10 цифр). Например: <i>1234 567890</i>."
        )
        return

    dialog_manager.dialog_data.setdefault("passport_form", {})
    dialog_manager.dialog_data["passport_form"]["passport_number"] = passport_number

    await dialog_manager.switch_to(PassportSG.car_number)


async def on_car_number_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработать ввод номера автомобиля."""
    cleaned = re.sub(r"\s+", "", text).upper()
    if cleaned and len(cleaned) < 5:
        await message.answer(
            "❌ Номер автомобиля должен содержать минимум 5 символов. "
            "Если автомобиля нет, нажми «Пропустить»."
        )
        return

    dialog_manager.dialog_data.setdefault("passport_form", {})
    dialog_manager.dialog_data["passport_form"]["car_number"] = cleaned or None

    await _save_passport_data(dialog_manager, message.from_user.id, message)


async def on_skip_car_number(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Пропустить ввод номера автомобиля."""
    dialog_manager.dialog_data.setdefault("passport_form", {})
    dialog_manager.dialog_data["passport_form"]["car_number"] = None

    await _save_passport_data(dialog_manager, callback.from_user.id, callback)


async def on_passport_back_to_menu(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    """Вернуться в главное меню."""
    dialog_manager.dialog_data.pop("passport_form", None)
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)
