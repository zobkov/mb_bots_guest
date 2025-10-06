"""Тестовый диалог для проверки синтаксиса."""
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button

from app.states import MainMenuSG


async def test_button_click(callback: CallbackQuery, button: Button, manager: DialogManager):
    """Тестовый обработчик кнопки."""
    await callback.message.answer("Кнопка работает!")


def create_test_dialog() -> Dialog:
    """Создать тестовый диалог."""
    return Dialog(
        Window(
            Const("Тестовое сообщение"),
            Button(
                Const("Тестовая кнопка"),
                id="test_btn",
                on_click=test_button_click,
            ),
            state=MainMenuSG.menu,
        ),
    )