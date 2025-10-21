"""Диалог главного меню."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button

from .handlers import (
    on_registration_click,
    on_faq_click,
    on_referral_click,
    on_passport_click,
)
from .getters import get_user_info
from ...states import MainMenuSG


def create_main_menu_dialog() -> Dialog:
    """Создать диалог главного меню."""
    return Dialog(
        Window(
            Format(
                "Привет, <b>{first_name}</b>! 👋\n\n"
                "Это бот для гостей конференции <b>Менеджмент Будущего</b>.\n"
                "Здесь ты можешь найти нужную информацию, оформить пропуск и зарегистрироваться на мероприятия.\n\n"
                "<b>ВНИМАНИЕ</b> \nЕсли ты не из СПбГУ, то необходимо заполнить данные в разделе <b>\"Данные для пропуска\"</b>"
            ),
            Button(
                Const("📝 Регистрация на мероприятия"),
                id="registration",
                on_click=on_registration_click,
            ),
            Button(
                Const("🛂 Данные для пропуска"),
                id="passport",
                on_click=on_passport_click,
            ),
            Button(
                Const("❓ Поддержка и вопросы"),
                id="faq",
                on_click=on_faq_click,
            ),
            Button(
                Const("🎁 Реферальная программа"),
                id="referral",
                on_click=on_referral_click,
            ),
            getter=get_user_info,
            state=MainMenuSG.menu,
        ),
    )