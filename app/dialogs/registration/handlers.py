"""Обработчики для диалога регистрации на мероприятия."""
from typing import Any

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select

from app.services.event_service import EventService
from app.services.user_service import UserService
from app.states import RegistrationSG, MainMenuSG


async def on_event_select(
    callback,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
    **kwargs
):
    """Обработчик выбора мероприятия для регистрации."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    telegram_id = callback.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if not user:
        await callback.message.answer("❌ Сначала необходимо пройти регистрацию.")
        return
    
    try:
        event_id = int(item_id)
        success, message = await event_service.register_user_for_event(user, event_id)
        
        if success:
            await callback.message.answer(f"✅ {message}")
        else:
            await callback.message.answer(f"❌ {message}")
            
    except ValueError:
        await callback.message.answer("❌ Ошибка: некорректный ID мероприятия.")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при регистрации: {str(e)}")


async def on_register_confirm(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик подтверждения регистрации (не используется в новой версии)."""
    pass


async def on_show_my_registrations(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик показа текущих регистраций."""
    await dialog_manager.switch_to(RegistrationSG.my_registrations)


async def on_unregister_event(
    callback,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
    **kwargs
):
    """Обработчик отмены регистрации на мероприятие."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    telegram_id = callback.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if not user:
        await callback.message.answer("❌ Пользователь не найден.")
        return
    
    try:
        event_id = int(item_id)
        success, message = await event_service.unregister_user_from_event(user, event_id)
        
        if success:
            await callback.message.answer(f"✅ {message}")
        else:
            await callback.message.answer(f"❌ {message}")
            
    except ValueError:
        await callback.message.answer("❌ Ошибка: некорректный ID мероприятия.")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при отмене регистрации: {str(e)}")


async def on_back_to_menu(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик возврата в главное меню."""
    await dialog_manager.start(MainMenuSG.menu, mode="reset_stack")