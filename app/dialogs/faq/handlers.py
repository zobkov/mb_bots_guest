"""Обработчики для диалога поддержки."""
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.states import MainMenuSG


async def on_back_to_menu(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик возврата в главное меню."""
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)