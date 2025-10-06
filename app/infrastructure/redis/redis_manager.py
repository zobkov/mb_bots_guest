"""Подключение к Redis для хранения состояния диалогов."""
import redis.asyncio as redis

from app.config.config import RedisConfig


class RedisManager:
    """Менеджер для работы с Redis."""
    
    def __init__(self, config: RedisConfig):
        self.config = config
        self._redis: redis.Redis = None
    
    async def get_redis(self) -> redis.Redis:
        """Получить подключение к Redis."""
        if self._redis is None:
            self._redis = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                decode_responses=True
            )
        return self._redis
    
    async def close(self):
        """Закрыть подключение к Redis."""
        if self._redis:
            await self._redis.close()