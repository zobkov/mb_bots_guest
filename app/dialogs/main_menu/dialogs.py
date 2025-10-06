"""Диалог главного меню."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button

from .handlers import on_registration_click, on_faq_click
from .getters import get_user_info
from ...states import MainMenuSG


def create_main_menu_dialog() -> Dialog:
    """Создать диалог главного меню."""
    return Dialog(
        Window(
            Format(
                "Привет, <b>{first_name}</b>! 👋\n\n"
                "Этот бот существует для гостей конференции <b>Менеджмент Будущего</b>. "
                "Здесь ты можешь найти нужную информацию и зарегистрироваться на мероприятия."
            ),
            Button(
                Const("📝 Регистрация на мероприятия"),
                id="registration",
                on_click=on_registration_click,
            ),
            Button(
                Const("❓ Поддержка и вопросы"),
                id="faq",
                on_click=on_faq_click,
            ),
            getter=get_user_info,
            state=MainMenuSG.menu,
        ),
    )