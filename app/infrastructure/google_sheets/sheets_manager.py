"""Менеджер для работы с Google Sheets."""
import logging
from typing import List, Optional
from datetime import datetime

import gspread
from google.auth.exceptions import GoogleAuthError

from app.config.config import GoogleSheetsConfig
from app.database.models.user import User

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    """Менеджер для работы с Google Sheets."""
    
    def __init__(self, config: GoogleSheetsConfig):
        self.config = config
        self._client: Optional[gspread.Client] = None
        self._spreadsheet: Optional[gspread.Spreadsheet] = None
    
    def _get_client(self) -> gspread.Client:
        """Получить клиент Google Sheets."""
        if self._client is None:
            try:
                self._client = gspread.service_account(filename=self.config.credentials_path)
            except GoogleAuthError as e:
                logger.error(f"Ошибка аутентификации Google Sheets: {e}")
                raise
            except Exception as e:
                logger.error(f"Ошибка создания клиента Google Sheets: {e}")
                raise
        return self._client
    
    def _get_spreadsheet(self) -> gspread.Spreadsheet:
        """Получить таблицу Google Sheets."""
        if self._spreadsheet is None:
            try:
                client = self._get_client()
                self._spreadsheet = client.open_by_url(self.config.spreadsheet_url)
            except Exception as e:
                logger.error(f"Ошибка открытия таблицы: {e}")
                raise
        return self._spreadsheet
    
    def _get_or_create_worksheet(self, sheet_name: str) -> gspread.Worksheet:
        """Получить или создать лист в таблице."""
        try:
            spreadsheet = self._get_spreadsheet()
            
            # Попробуем найти существующий лист
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                logger.info(f"Найден существующий лист: {sheet_name}")
                return worksheet
            except gspread.WorksheetNotFound:
                # Создаем новый лист
                logger.info(f"Создаем новый лист: {sheet_name}")
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                
                # Добавляем заголовки
                headers = [
                    "Дата регистрации",
                    "Имя", 
                    "Фамилия", 
                    "Email", 
                    "Место работы/учебы",
                    "Telegram ID"
                ]
                worksheet.append_row(headers)
                
                return worksheet
                
        except Exception as e:
            logger.error(f"Ошибка при работе с листом {sheet_name}: {e}")
            raise
    
    async def add_user_to_general_sheet(self, user: User) -> bool:
        """Добавить пользователя на общий лист (general)."""
        try:
            worksheet = self._get_or_create_worksheet("general")
            
            # Формируем строку данных
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user.first_name,
                user.last_name,
                user.email,
                user.workplace,
                str(user.telegram_id)
            ]
            
            worksheet.append_row(row_data)
            logger.info(f"Пользователь {user.first_name} {user.last_name} добавлен в общий лист")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя в общий лист: {e}")
            return False
    
    async def add_user_to_event_sheet(self, user: User, event_name: str, sheet_name: str) -> bool:
        """Добавить пользователя на лист мероприятия."""
        try:
            worksheet = self._get_or_create_worksheet(sheet_name)
            
            # Формируем строку данных
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user.first_name,
                user.last_name,
                user.email,
                user.workplace,
                str(user.telegram_id)
            ]
            
            worksheet.append_row(row_data)
            logger.info(f"Пользователь {user.first_name} {user.last_name} добавлен на лист мероприятия {event_name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя на лист мероприятия {event_name}: {e}")
            return False
    
    async def remove_user_from_event_sheet(self, user: User, sheet_name: str) -> bool:
        """Удалить пользователя с листа мероприятия."""
        try:
            worksheet = self._get_or_create_worksheet(sheet_name)
            
            # Ищем строку с пользователем по Telegram ID
            all_records = worksheet.get_all_records()
            
            for i, record in enumerate(all_records, start=2):  # Начинаем с 2, так как 1 - заголовки
                if str(record.get("Telegram ID", "")) == str(user.telegram_id):
                    worksheet.delete_rows(i)
                    logger.info(f"Пользователь {user.first_name} {user.last_name} удален с листа {sheet_name}")
                    return True
            
            logger.warning(f"Пользователь {user.first_name} {user.last_name} не найден на листе {sheet_name}")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка удаления пользователя с листа мероприятия: {e}")
            return False