"""Диалог реферальной программы."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button

from .getters import get_referral_dashboard
from .handlers import on_share_link, on_back_to_menu
from ...states import ReferralSG


def create_referral_dialog() -> Dialog:
    """Создать диалог для отображения реферальной программы."""
    return Dialog(
        Window(
            Format(
                "🎯 <b>Реферальная программа</b>\n\n"
                "🔗 <b>Твоя ссылка:</b>\n"
                "<code>{referral_link}</code>\n\n"
                "<b>Приглашено:</b> {invite_count}\n"
                "<b>Твоя позиция:</b> {rank_text}\n\n"
                "⚠️ Баллы начисляются после регистрации приглашённого на выступление Мордашова.\n\n"
                "🏆 <b>Лидеры:</b>\n{leaders_text}\n\n"
                "Список подарков за первое, второе и третье места появится здесь позже."
            ),
            Button(
                Const("📤 Отправить ссылку"),
                id="share_ref_link",
                on_click=on_share_link,
            ),
            Button(
                Const("🔙 Назад"),
                id="referral_back",
                on_click=on_back_to_menu,
            ),
            getter=get_referral_dashboard,
            state=ReferralSG.dashboard,
        ),
    )
