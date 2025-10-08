#!/usr/bin/env python3
"""Тестовый скрипт для проверки системы блокировки."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from app.config.config import load_config
from app.infrastructure.redis.redis_manager import RedisManager
from app.services.lock_service import LockService


async def test_lock_system():
    """Тестирует систему блокировки."""
    print("🧪 Тестирование системы блокировки...")
    
    try:
        # Загружаем конфигурацию
        config = load_config()
        print(f"✅ Конфигурация загружена. Админы: {config.bot.admin_ids}")
        
        # Создаем Redis менеджер
        redis_manager = RedisManager(config.redis)
        redis_client = await redis_manager.get_redis()
        
        # Проверяем подключение к Redis
        await redis_client.ping()
        print(f"✅ Подключение к Redis установлено: {config.redis.host}:{config.redis.port}")
        
        # Создаем сервис блокировки
        lock_service = LockService(redis_client)
        
        # Тестируем функции блокировки
        print("\n📋 Тестирование функций:")
        
        # Проверяем текущее состояние
        initial_state = await lock_service.is_locked()
        print(f"1. Текущее состояние блокировки: {'🔒 Заблокирован' if initial_state else '🔓 Разблокирован'}")
        
        # Переключаем состояние
        success, new_state = await lock_service.toggle_lock()
        if success:
            print(f"2. Переключение успешно: {'🔒 Заблокирован' if new_state else '🔓 Разблокирован'}")
        else:
            print("2. ❌ Ошибка при переключении")
            
        # Проверяем новое состояние
        current_state = await lock_service.is_locked()
        print(f"3. Проверка состояния: {'🔒 Заблокирован' if current_state else '🔓 Разблокирован'}")
        
        # Возвращаем в исходное состояние
        await lock_service.set_lock(initial_state)
        final_state = await lock_service.is_locked()
        print(f"4. Возврат к исходному состоянию: {'🔒 Заблокирован' if final_state else '🔓 Разблокирован'}")
        
        # Закрываем соединение
        await redis_client.aclose()
        
        print("\n✅ Тестирование завершено успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_lock_system())
    if not success:
        sys.exit(1)