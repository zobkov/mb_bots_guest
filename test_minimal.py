#!/usr/bin/env python3
"""Минимальный тест для проверки диалогов."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs

from app.config.config import load_config
from app.dialogs.main_menu.dialogs import create_main_menu_dialog


async def test_dialog():
    """Тест диалога."""
    config = load_config()
    
    # Создаем бота с memory storage для теста
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    # Создаем диалог
    dialog = create_main_menu_dialog()
    dp.include_router(dialog)
    
    # Настраиваем aiogram-dialog
    setup_dialogs(dp)
    
    print("✅ Диалог создан успешно!")
    
    await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(test_dialog())
        print("✅ Тест прошел успешно!")
    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()