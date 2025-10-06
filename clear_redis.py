#!/usr/bin/env python3
"""Скрипт для очистки Redis от старых состояний диалогов."""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.config.config import load_config
from redis.asyncio import Redis


async def clear_redis():
    """Очистить Redis от старых состояний."""
    config = load_config()
    
    if config.redis.password:
        redis_url = f"redis://:{config.redis.password}@{config.redis.host}:{config.redis.port}/0"
    else:
        redis_url = f"redis://{config.redis.host}:{config.redis.port}/0"
    
    redis_client = Redis.from_url(redis_url)
    
    try:
        # Получаем все ключи
        keys = await redis_client.keys("*")
        
        if keys:
            print(f"🗑️ Найдено {len(keys)} ключей в Redis")
            
            # Удаляем все ключи
            await redis_client.delete(*keys)
            print("✅ Все ключи удалены из Redis")
        else:
            print("ℹ️ Redis пуст")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке Redis: {e}")
    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    print("🧹 Очистка Redis...")
    asyncio.run(clear_redis())
    print("🎉 Готово!")