"""Обработчики для главного меню."""
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.states import RegistrationSG, FaqSG
from app.services.user_service import UserService
from app.services.event_service import EventService


async def on_registration_click(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик нажатия на кнопку регистрации."""
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    
    telegram_id = callback.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if not user:
        await callback.message.answer("❌ Сначала необходимо пройти регистрацию.")
        return
    
    # Проверяем, есть ли у пользователя активные регистрации
    registrations = await event_service.get_user_registrations(user.id)
    
    dialog_manager.show_mode = ShowMode.SEND
    
    if registrations:
        # Если есть регистрации, сразу переходим к их просмотру
        await dialog_manager.start(RegistrationSG.my_registrations)
    else:
        # Если нет регистраций, начинаем процесс регистрации
        await dialog_manager.start(RegistrationSG.optional_events)


async def on_faq_click(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик нажатия на кнопку поддержки."""
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.start(FaqSG.faq)