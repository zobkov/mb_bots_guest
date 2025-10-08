"""Диалог поддержки и FAQ."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button

from .handlers import on_back_to_menu
from ...states import FaqSG


def create_faq_dialog() -> Dialog:
    """Создать диалог поддержки."""
    return Dialog(
        Window(
            Const(
                "❓ <b>Поддержка и вопросы</b>\n\n"
                "📧 По всем вопросам обращайтесь на:\n"
                "<b>program@mb-conference.ru</b>\n\n"
                "По тех. вопросам, связанных с ботом, обращайтесь к Артёму @zobko"
                "❓ <b>Часто задаваемые вопросы:</b>\n\n"
            ),
            Button(
                Const("🔙 Назад в меню"),
                id="back_to_menu",
                on_click=on_back_to_menu,
            ),
            state=FaqSG.faq,
        ),
    )