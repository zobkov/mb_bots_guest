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
            is_locked = result == "true"
            logger.debug(f"Проверка блокировки: ключ={self.LOCK_KEY}, значение={result}, результат={is_locked}")
            return is_locked
        except Exception as e:
            logger.error(f"Ошибка при проверке блокировки: {e}")
            return False
    
    async def set_lock(self, locked: bool) -> bool:
        """Устанавливает режим блокировки."""
        try:
            value = "true" if locked else "false"
            await self.redis.set(self.LOCK_KEY, value)
            logger.info(f"Режим блокировки {'включен' if locked else 'выключен'} (установлено значение: {value})")
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