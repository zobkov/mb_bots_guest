#!/usr/bin/env python3
"""Утилита для управления блокировкой бота из командной строки."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from app.config.config import load_config
from app.infrastructure.redis.redis_manager import RedisManager
from app.services.lock_service import LockService


async def manage_lock():
    """Управление блокировкой бота."""
    if len(sys.argv) != 2 or sys.argv[1] not in ['status', 'on', 'off', 'toggle']:
        print("Использование:")
        print("  python3 manage_lock.py status   - показать текущий статус")
        print("  python3 manage_lock.py on       - включить блокировку")
        print("  python3 manage_lock.py off      - выключить блокировку")
        print("  python3 manage_lock.py toggle   - переключить блокировку")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        # Загружаем конфигурацию и подключаемся к Redis
        config = load_config()
        redis_manager = RedisManager(config.redis)
        redis_client = await redis_manager.get_redis()
        
        # Проверяем подключение
        await redis_client.ping()
        
        # Создаем сервис блокировки
        lock_service = LockService(redis_client)
        
        if command == 'status':
            is_locked = await lock_service.is_locked()
            status = "🔒 ЗАБЛОКИРОВАН" if is_locked else "🔓 РАЗБЛОКИРОВАН"
            print(f"Текущий статус блокировки: {status}")
            
        elif command == 'on':
            success = await lock_service.set_lock(True)
            if success:
                print("🔒 Блокировка ВКЛЮЧЕНА")
            else:
                print("❌ Ошибка при включении блокировки")
                
        elif command == 'off':
            success = await lock_service.set_lock(False)
            if success:
                print("🔓 Блокировка ВЫКЛЮЧЕНА")
            else:
                print("❌ Ошибка при выключении блокировки")
                
        elif command == 'toggle':
            success, new_state = await lock_service.toggle_lock()
            if success:
                status = "🔒 ЗАБЛОКИРОВАН" if new_state else "🔓 РАЗБЛОКИРОВАН"
                print(f"Блокировка переключена: {status}")
            else:
                print("❌ Ошибка при переключении блокировки")
        
        # Закрываем соединение
        await redis_client.aclose()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(manage_lock())