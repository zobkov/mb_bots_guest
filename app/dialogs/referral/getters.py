"""Геттеры для диалога реферальной программы."""
from typing import Any, Dict

from aiogram_dialog import DialogManager

from app.services.referral_service import ReferralService
from app.services.user_service import UserService


async def get_referral_dashboard(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Сформировать данные для экрана реферальной программы."""
    referral_service: ReferralService = dialog_manager.middleware_data["referral_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    bot = dialog_manager.middleware_data.get("bot")
    if bot is None and hasattr(dialog_manager.event, "bot"):
        bot = dialog_manager.event.bot

    telegram_id = dialog_manager.event.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)

    if not user:
        return {
            "referral_link": "Стань участником, чтобы получить ссылку",
            "invite_count": 0,
            "rank_text": "―",
            "leaders_text": "Список появится позже",
            "has_leaders": False,
        }

    referral_link = await referral_service.get_invite_link(bot, user)
    stats = await referral_service.get_stats(user)

    if stats.rank:
        rank_text = f"{stats.rank} из {stats.total_participants}" if stats.total_participants else f"#{stats.rank}"
    else:
        rank_text = "Пока вне рейтинга"

    if stats.leaders:
        leaders_lines = [
            f"{entry.rank}. {entry.full_name or 'Участник'} — {entry.invite_count}"
            for entry in stats.leaders
        ]
        leaders_text = "\n".join(leaders_lines)
    else:
        leaders_text = "Лидеров пока нет — стань первым!"

    return {
        "referral_link": referral_link,
        "invite_count": stats.invite_count,
        "rank_text": rank_text,
        "leaders_text": leaders_text,
        "has_leaders": bool(stats.leaders),
    }
