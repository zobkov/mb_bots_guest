"""Обработчики для главного меню."""
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from app.states import RegistrationSG, FaqSG


async def on_registration_click(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик нажатия на кнопку регистрации."""
    await dialog_manager.start(RegistrationSG.events_list)


async def on_faq_click(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик нажатия на кнопку поддержки."""
    await dialog_manager.start(FaqSG.faq)