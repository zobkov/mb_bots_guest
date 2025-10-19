"""Обработчики кнопок диалога реферальной программы."""
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.services.referral_service import ReferralService
from app.services.user_service import UserService
from app.states import MainMenuSG


async def on_share_link(callback, button: Button, dialog_manager: DialogManager):
    """Отправить пользователю его реферальную ссылку в отдельном сообщении."""
    referral_service: ReferralService = dialog_manager.middleware_data["referral_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    bot = dialog_manager.middleware_data.get("bot") or callback.bot

    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Сначала завершите регистрацию", show_alert=True)
        return

    link = await referral_service.get_invite_link(bot, user)
    await callback.answer("Ссылка отправлена")
    await callback.message.answer(
        "Вот твоя персональная ссылка:\n"
        f"{link}\n\n"
        "Поделись ей с друзьями, и они попадут на страницу регистрации с твоим кодом.",
        disable_web_page_preview=True,
    )


async def on_back_to_menu(callback, button: Button, dialog_manager: DialogManager):
    """Вернуться в главное меню."""
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)
