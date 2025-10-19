"""Репозиторий для работы с пользователями."""
from typing import Optional, List

import secrets
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.database.models.registration import EventRegistration
from app.database.models.user import User


class UserRepository:
    """Репозиторий для работы с пользователями."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        telegram_id: int,
        first_name: str,
        last_name: str,
        email: str,
        workplace: str,
        username: str = None
    ) -> User:
        """Создать нового пользователя с уникальным реферальным кодом."""
        referral_code = await self._generate_unique_referral_code()
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            workplace=workplace,
            referral_code=referral_code,
        )
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def update(
        self,
        user: User,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        workplace: str = None,
        username: str = None
    ) -> User:
        """Обновить данные пользователя."""
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email
        if workplace is not None:
            user.workplace = workplace
        if username is not None:
            user.username = username
        
        await self.session.flush()
        return user

    async def get_by_referral_code(self, referral_code: str) -> Optional[User]:
        """Получить пользователя по реферальному коду."""
        stmt = select(User).where(User.referral_code == referral_code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_referral_code(self, user: User) -> User:
        """Убедиться, что у пользователя есть реферальный код."""
        if not user.referral_code:
            user.referral_code = await self._generate_unique_referral_code()
            await self.session.flush()
        return user

    async def count_referrals(self, user_id: int, target_event_ids: List[int]) -> int:
        """Подсчитать количество приглашенных пользователем, завершивших целевую регистрацию."""
        if not target_event_ids:
            return 0

        invitee_alias = aliased(User)
        stmt = (
            select(func.count(func.distinct(EventRegistration.user_id)))
            .select_from(EventRegistration)
            .join(invitee_alias, invitee_alias.id == EventRegistration.user_id)
            .where(
                invitee_alias.referrer_id == user_id,
                EventRegistration.event_id.in_(target_event_ids),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def set_referrer(self, user: User, referrer: User) -> User:
        """Назначить пригласившего пользователя."""
        user.referrer_id = referrer.id
        await self.session.flush()
        return user

    async def get_referral_leaderboard(self, target_event_ids: List[int]) -> List[tuple[int, str, str, int]]:
        """Получить рейтинг пользователей по количеству подтверждённых приглашённых."""
        if not target_event_ids:
            return []

        invitee_alias = aliased(User)
        registration_alias = aliased(EventRegistration)
        confirmed_count = func.count(func.distinct(registration_alias.user_id))
        stmt = (
            select(
                User.id,
                User.first_name,
                User.last_name,
                confirmed_count,
                User.created_at,
            )
            .outerjoin(invitee_alias, invitee_alias.referrer_id == User.id)
            .outerjoin(
                registration_alias,
                (registration_alias.user_id == invitee_alias.id)
                & (registration_alias.event_id.in_(target_event_ids)),
            )
            .group_by(User.id, User.first_name, User.last_name, User.created_at)
            .order_by(confirmed_count.desc(), User.created_at.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [(row[0], row[1], row[2], row[3]) for row in rows]

    async def mark_referral_notified(self, user: User, notified: bool = True) -> User:
        """Обновить флаг уведомления о реферальной программе."""
        user.referral_notified = notified
        await self.session.flush()
        return user

    async def _generate_unique_referral_code(self) -> str:
        """Сгенерировать уникальный реферальный код."""
        while True:
            candidate = secrets.token_urlsafe(6)
            candidate = candidate.replace("-", "").replace("_", "")[:10]
            stmt = select(User.id).where(User.referral_code == candidate)
            result = await self.session.execute(stmt)
            if result.scalar_one_or_none() is None:
                return candidate