"""Настройки конфигурации бота."""
import os
from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных."""
    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def url(self) -> str:
        """Возвращает URL для подключения к базе данных."""
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_url(self) -> str:
        """Возвращает асинхронный URL для подключения к базе данных."""
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class RedisConfig:
    """Конфигурация Redis."""
    host: str
    port: int
    password: Optional[str] = None


@dataclass
class GoogleSheetsConfig:
    """Конфигурация Google Sheets."""
    credentials_path: str
    spreadsheet_url: str


@dataclass
class BotConfig:
    """Основная конфигурация бота."""
    token: str
    log_level: str
    admin_ids: list[int]


@dataclass
class Config:
    """Общая конфигурация приложения."""
    bot: BotConfig
    database: DatabaseConfig
    redis: RedisConfig
    google_sheets: GoogleSheetsConfig


def load_config() -> Config:
    """Загружает конфигурацию из переменных окружения."""
    env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            token=env.str("BOT_TOKEN"),
            log_level=env.str("LOG_LEVEL", "INFO"),
            admin_ids=[int(id_str.strip()) for id_str in env.str("BOT_ADMIN_IDS", "257026813").split(",")]
        ),
        database=DatabaseConfig(
            host=env.str("DB_HOST"),
            port=env.int("DB_PORT"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASS"),
            database=env.str("DB_NAME")
        ),
        redis=RedisConfig(
            host=env.str("REDIS_HOST"),
            port=env.int("REDIS_PORT"),
            password=env.str("REDIS_PASSWORD", None) if env.str("REDIS_PASSWORD", "") else None
        ),
        google_sheets=GoogleSheetsConfig(
            credentials_path=env.str("GOOGLE_CREDENTIALS_PATH"),
            spreadsheet_url=env.str("GOOGLE_SPREADSHEET_URL")
        )
    )