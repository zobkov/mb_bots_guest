"""Обработчики для диалога регистрации."""
import re
from typing import Any

from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from app.services.user_service import UserService
from app.states import StartSG, MainMenuSG


async def on_start_registration(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик начала регистрации."""
    await dialog_manager.next()


async def on_first_name_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработчик ввода имени."""
    if not text.strip():
        await message.answer("❌ Имя не может быть пустым. Попробуйте еще раз.")
        return
    
    if len(text.strip()) < 2:
        await message.answer("❌ Имя должно содержать минимум 2 символа. Попробуйте еще раз.")
        return
    
    dialog_manager.dialog_data["first_name"] = text.strip()
    await dialog_manager.next()


async def on_last_name_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработчик ввода фамилии."""
    if not text.strip():
        await message.answer("❌ Фамилия не может быть пустой. Попробуйте еще раз.")
        return
    
    if len(text.strip()) < 2:
        await message.answer("❌ Фамилия должна содержать минимум 2 символа. Попробуйте еще раз.")
        return
    
    dialog_manager.dialog_data["last_name"] = text.strip()
    await dialog_manager.next()


async def on_email_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработчик ввода email."""
    email = text.strip().lower()
    
    # Простая валидация email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await message.answer("❌ Неверный формат email. Попробуйте еще раз.")
        return
    
    dialog_manager.dialog_data["email"] = email
    await dialog_manager.next()


async def on_workplace_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    """Обработчик ввода места работы/учебы."""
    if not text.strip():
        await message.answer("❌ Место работы/учёбы не может быть пустым. Попробуйте еще раз.")
        return
    
    if len(text.strip()) < 2:
        await message.answer("❌ Место работы/учёбы должно содержать минимум 2 символа. Попробуйте еще раз.")
        return
    
    dialog_manager.dialog_data["workplace"] = text.strip()
    await dialog_manager.next()


async def on_restart_registration(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик перезапуска регистрации."""
    # Очищаем данные
    dialog_manager.dialog_data.clear()
    # Переходим к вводу имени
    await dialog_manager.switch_to(StartSG.first_name)


async def on_confirm_registration(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик подтверждения регистрации."""
    # Получаем данные из контекста
    context = dialog_manager.dialog_data
    telegram_id = callback.from_user.id
    
    # Получаем сервис пользователей
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    try:
        # Создаем или обновляем пользователя
        user = await user_service.get_or_create_user(
            telegram_id=telegram_id,
            first_name=context["first_name"],
            last_name=context["last_name"],
            email=context["email"],
            workplace=context["workplace"]
        )
        
        # Переходим в главное меню
        await dialog_manager.start(MainMenuSG.menu, mode="reset_stack")
        
    except Exception as e:
        await callback.message.answer(f"❌ Произошла ошибка при регистрации: {str(e)}")
        # Остаемся в том же состоянии для повторной попытки