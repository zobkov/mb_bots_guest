"""Основные обработчики команд."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from app.states import StartSG, MainMenuSG
from app.services.user_service import UserService

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, dialog_manager: DialogManager, user_service: UserService):
    """Обработчик команды /start."""
    telegram_id = message.from_user.id
    
    # Проверяем, зарегистрирован ли пользователь
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if user:
        # Пользователь уже зарегистрирован, переходим в главное меню
        await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)
    else:
        # Новый пользователь, начинаем регистрацию
        await dialog_manager.start(StartSG.welcome, mode=StartMode.RESET_STACK)