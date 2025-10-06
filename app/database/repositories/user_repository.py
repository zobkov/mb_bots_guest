"""Репозиторий для работы с пользователями."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        """Создать нового пользователя."""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            workplace=workplace
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