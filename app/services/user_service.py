"""Сервис для работы с пользователями."""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.repositories.user_repository import UserRepository
from app.infrastructure.google_sheets.sheets_manager import GoogleSheetsManager


class UserService:
    """Сервис для работы с пользователями."""
    
    def __init__(self, session: AsyncSession, sheets_manager: GoogleSheetsManager):
        self.repository = UserRepository(session)
        self.sheets_manager = sheets_manager
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        first_name: str,
        last_name: str,
        email: str,
        workplace: str
    ) -> User:
        """Получить пользователя или создать нового."""
        # Проверяем, существует ли пользователь
        user = await self.repository.get_by_telegram_id(telegram_id)
        
        if user:
            # Обновляем данные пользователя
            user = await self.repository.update(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                workplace=workplace
            )
        else:
            # Создаем нового пользователя
            user = await self.repository.create(
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                workplace=workplace
            )
            
            # Добавляем в Google Sheets на общий лист
            await self.sheets_manager.add_user_to_general_sheet(user)
        
        return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id."""
        return await self.repository.get_by_telegram_id(telegram_id)