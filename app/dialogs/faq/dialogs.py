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
                "📞 Или звоните по номеру:\n"
                "<b>+7 (XXX) XXX-XX-XX</b>\n\n"
                "🕐 Время работы поддержки:\n"
                "Пн-Пт: 9:00 — 18:00 (МСК)\n\n"
                "📍 Адрес проведения конференции:\n"
                "г. Москва, ...\n\n"
                "❓ <b>Часто задаваемые вопросы:</b>\n\n"
                "<b>В: Как отменить регистрацию?</b>\n"
                "О: Перейдите в раздел 'Мои регистрации' и нажмите на нужное мероприятие.\n\n"
                "<b>В: Можно ли зарегистрироваться на несколько мероприятий одновременно?</b>\n"
                "О: Да, кроме мероприятий, которые проходят в одно время (13:10-14:30).\n\n"
                "<b>В: Что делать, если места закончились?</b>\n"
                "О: Обратитесь в поддержку, возможно, появятся свободные места."
            ),
            Button(
                Const("🔙 Назад в меню"),
                id="back_to_menu",
                on_click=on_back_to_menu
            ),
            state=FaqSG.faq,
        ),
    )