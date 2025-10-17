"""Основные обработчики команд."""
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
import redis.asyncio as redis

from app.states import StartSG, MainMenuSG
from app.services.user_service import UserService
from app.services.lock_service import LockService
from app.filters import IsAdminFilter
from app.utils.logger import get_logger

logger = get_logger(__name__)
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


@router.message(Command("menu"))
async def menu_command(message: Message, dialog_manager: DialogManager):
    """Обработчик команды /menu для открытия главного меню."""
    await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)


@router.callback_query(F.data == "open_main_menu")
async def menu_button_handler(callback: CallbackQuery, dialog_manager: DialogManager):
    """Обработчик кнопки "Главное меню" из широковещательных сообщений."""
    await callback.answer()
    await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)


@router.message(Command("lock"), IsAdminFilter())
async def lock_command(message: Message, redis_client: redis.Redis):
    """Обработчик команды /lock для переключения режима блокировки."""
    # Redis клиент должен передаваться через dependency injection
    lock_service = LockService(redis_client)
    
    try:
        success, new_state = await lock_service.toggle_lock()
        
        if success:
            status_text = "🔒 <b>ЗАБЛОКИРОВАН</b>" if new_state else "🔓 <b>РАЗБЛОКИРОВАН</b>"
            description = (
                "Все пользователи (кроме админов) получают уведомление о технических работах."
                if new_state else 
                "Бот работает в обычном режиме."
            )
            
            await message.answer(
                f"🔧 <b>Режим блокировки изменен</b>\n\n"
                f"Статус: {status_text}\n"
                f"Описание: {description}\n\n"
                f"👤 Изменение внес: {message.from_user.first_name}"
            )
            
            logger.info(
                f"Админ {message.from_user.id} ({message.from_user.first_name}) "
                f"{'включил' if new_state else 'выключил'} режим блокировки"
            )
        else:
            await message.answer(
                "❌ <b>Ошибка</b>\n\n"
                "Не удалось изменить режим блокировки.\n"
                "Проверьте подключение к Redis."
            )
            
    except Exception as e:
        logger.error(f"Ошибка в команде /lock: {e}")
        await message.answer(
            "❌ <b>Ошибка</b>\n\n"
            "Произошла ошибка при выполнении команды."
        )