"""Обработчики для диалога поддержки."""
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from app.states import MainMenuSG


async def on_back_to_menu(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик возврата в главное меню."""
    await dialog_manager.start(MainMenuSG.menu, mode="reset_stack")