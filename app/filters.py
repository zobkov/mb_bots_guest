"""Фильтры для проверки доступа."""
from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.config.config import load_config


class IsAdminFilter(BaseFilter):
    """Фильтр для проверки, является ли пользователь администратором."""
    
    def __init__(self):
        self.config = load_config()
    
    async def __call__(self, message: Message) -> bool:
        """Проверяет, является ли отправитель администратором."""
        return message.from_user.id in self.config.bot.admin_ids