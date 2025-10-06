"""Конфигурация логирования для бота."""
import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Настройка системы логирования с разделением по дням и категориям."""
    # Создаем директории для логов
    logs_dir = Path("logs")
    errors_dir = logs_dir / "errors"
    general_dir = logs_dir / "general"
    
    for directory in [logs_dir, errors_dir, general_dir]:
        directory.mkdir(exist_ok=True)
    
    # Получаем текущую дату для имени файла
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Файлы логов
    error_log_file = errors_dir / f"errors_{current_date}.log"
    general_log_file = general_dir / f"general_{current_date}.log"
    
    # Очищаем предыдущие обработчики
    logging.getLogger().handlers.clear()
    
    # Создаем форматтер
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Консольный обработчик (только для INFO и выше)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Общий файловый обработчик (все уровни)
    general_handler = logging.FileHandler(general_log_file, encoding="utf-8")
    general_handler.setLevel(logging.DEBUG)
    general_handler.setFormatter(formatter)
    root_logger.addHandler(general_handler)
    
    # Файловый обработчик для ошибок (только ERROR и CRITICAL)
    error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Настраиваем специальные логгеры для aiogram
    aiogram_logger = logging.getLogger("aiogram")
    aiogram_logger.setLevel(logging.INFO)
    
    # Логгер для диалогов
    dialog_logger = logging.getLogger("aiogram_dialog")
    dialog_logger.setLevel(logging.INFO)
    
    # Логгер для нашего приложения
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.DEBUG)
    
    return root_logger


def get_logger(name: str = None) -> logging.Logger:
    """Получить логгер с указанным именем."""
    if name:
        return logging.getLogger(name)
    return logging.getLogger()


class ContextLogger:
    """Контекстный логгер для добавления дополнительной информации."""
    
    def __init__(self, logger: logging.Logger, context: dict = None):
        self.logger = logger
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Форматировать сообщение с контекстом."""
        if self.context:
            context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"[{context_str}] {message}"
        return message
    
    def debug(self, message: str, **kwargs):
        """Логировать DEBUG сообщение."""
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs):
        """Логировать INFO сообщение."""
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Логировать WARNING сообщение."""
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs):
        """Логировать ERROR сообщение."""
        self.logger.error(self._format_message(message), **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Логировать CRITICAL сообщение."""
        self.logger.critical(self._format_message(message), **kwargs)