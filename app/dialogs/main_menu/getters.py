"""Геттеры для главного меню."""
from typing import Dict, Any

from aiogram_dialog import DialogManager

from app.services.user_service import UserService


async def get_user_info(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получить информацию о пользователе."""
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    telegram_id = dialog_manager.event.from_user.id
    
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if user:
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "workplace": user.workplace
        }
    else:
        return {
            "first_name": "Гость",
            "last_name": "",
            "email": "",
            "workplace": ""
        }