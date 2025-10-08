"""Сервис для управления блокировкой бота."""
import redis.asyncio as redis
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


class LockService:
    """Сервис для управления режимом блокировки бота."""
    
    LOCK_KEY = "bot:lock_mode"
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def is_locked(self) -> bool:
        """Проверяет, заблокирован ли бот."""
        try:
            result = await self.redis.get(self.LOCK_KEY)
            return result == "true"
        except Exception as e:
            logger.error(f"Ошибка при проверке блокировки: {e}")
            return False
    
    async def set_lock(self, locked: bool) -> bool:
        """Устанавливает режим блокировки."""
        try:
            await self.redis.set(self.LOCK_KEY, "true" if locked else "false")
            logger.info(f"Режим блокировки {'включен' if locked else 'выключен'}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при установке блокировки: {e}")
            return False
    
    async def toggle_lock(self) -> tuple[bool, bool]:
        """Переключает режим блокировки. Возвращает (успех, новое_состояние)."""
        try:
            current_state = await self.is_locked()
            new_state = not current_state
            success = await self.set_lock(new_state)
            return success, new_state
        except Exception as e:
            logger.error(f"Ошибка при переключении блокировки: {e}")
            return False, False