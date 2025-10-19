"""Сервис для работы с реферальной программой."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.registration import Event
from app.database.models.user import User
from app.database.repositories.event_repository import EventRepository
from app.database.repositories.user_repository import UserRepository


REFERRAL_EVENT_KEYWORDS = ("мордашов", "mordashov", "костин", "kostin")


@dataclass
class ReferralLeaderboardEntry:
    """Запись в таблице лидеров реферальной программы."""
    rank: int
    full_name: str
    invite_count: int


@dataclass
class ReferralStats:
    """Статистика реферальной программы для пользователя."""
    invite_count: int
    rank: Optional[int]
    total_participants: int
    leaders: List[ReferralLeaderboardEntry]


class ReferralService:
    """Сервис для управления реферальной программой."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.event_repository = EventRepository(session)
        self._bot_username_cache: Optional[str] = None

    async def ensure_user_has_referral_code(self, user: User) -> str:
        """Убедиться, что у пользователя есть реферальный код и вернуть его."""
        user = await self.user_repository.ensure_referral_code(user)
        return user.referral_code

    async def apply_referral_code(self, user: User, referral_code: Optional[str]) -> None:
        """Назначить пригласившего пользователя по коду, если это возможно."""
        if not referral_code or not user:
            return

        cleaned_code = referral_code.strip()
        if not cleaned_code or user.referrer_id:
            return

        referrer = await self.user_repository.get_by_referral_code(cleaned_code)
        if not referrer or referrer.id == user.id:
            return

        await self.user_repository.set_referrer(user, referrer)
        await self.session.flush()

    async def get_invite_link(self, bot: Bot, user: User) -> str:
        """Получить персональную ссылку на бота для приглашений."""
        code = await self.ensure_user_has_referral_code(user)
        username = await self._get_bot_username(bot)
        return f"https://t.me/{username}?start={code}"

    async def get_stats(self, user: User, top_limit: int = 5) -> ReferralStats:
        """Получить статистику по реферальной программе для пользователя."""
        target_event_ids = await self._get_target_event_ids()
        leaderboard = await self.user_repository.get_referral_leaderboard(target_event_ids)
        leaders: List[ReferralLeaderboardEntry] = []
        invite_count = 0
        rank: Optional[int] = None

        for position, (user_id, first_name, last_name, count) in enumerate(leaderboard, start=1):
            if position <= top_limit and count > 0:
                leaders.append(
                    ReferralLeaderboardEntry(
                        rank=position,
                        full_name=" ".join(filter(None, [first_name, last_name])).strip(),
                        invite_count=count,
                    )
                )
            if user_id == user.id:
                invite_count = count
                if count > 0:
                    rank = position

        if rank is None and target_event_ids:
            invite_count = await self.user_repository.count_referrals(user.id, target_event_ids)

        total_participants = sum(1 for row in leaderboard if row[3] > 0)
        return ReferralStats(
            invite_count=invite_count,
            rank=rank,
            total_participants=total_participants,
            leaders=leaders,
        )

    def should_notify_for_event(self, event: Event) -> bool:
        """Определить, активирует ли мероприятие рассылку о реферальной программе."""
        return self._is_target_event(event)

    async def was_notified(self, user: User) -> bool:
        """Проверить, отправляли ли уведомление пользователю."""
        return bool(user.referral_notified)

    async def mark_notified(self, user: User) -> None:
        """Отметить, что уведомление отправлено."""
        await self.user_repository.mark_referral_notified(user, True)

    async def reset_notification(self, user: User) -> None:
        """Сбросить флаг уведомления (на случай повторной отправки)."""
        await self.user_repository.mark_referral_notified(user, False)

    async def _get_bot_username(self, bot: Bot) -> str:
        """Получить имя пользователя бота и закешировать его на время запроса."""
        if not self._bot_username_cache:
            me = await bot.get_me()
            if not me.username:
                raise RuntimeError("Bot username is not set. Установите username в BotFather")
            self._bot_username_cache = me.username
        return self._bot_username_cache

    async def _get_target_event_ids(self) -> List[int]:
        events = await self.event_repository.get_all_events()
        return [event.id for event in events if self._is_target_event(event)]

    def _is_target_event(self, event: Event) -> bool:
        haystacks = [
            (event.name or "").lower(),
            (event.description or "").lower(),
            (getattr(event, "sheet_name", "") or "").lower(),
        ]
        return any(keyword in haystack for haystack in haystacks for keyword in REFERRAL_EVENT_KEYWORDS)