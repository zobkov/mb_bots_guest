"""Геттеры для диалога регистрации."""
from typing import Dict, Any

from aiogram_dialog import DialogManager


async def get_user_data(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получить данные пользователя из контекста диалога."""
    context = dialog_manager.dialog_data
    
    return {
        "first_name": context.get("first_name", ""),
        "last_name": context.get("last_name", ""),
        "email": context.get("email", ""),
        "workplace": context.get("workplace", "")
    }