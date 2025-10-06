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
                
                # Проверим, есть ли заголовки (первая строка)
                try:
                    first_row = worksheet.row_values(1)
                    if not first_row or len(first_row) < 7:  # Изменено с 6 на 7 для Username
                        # Если заголовков нет или их мало, добавим
                        headers = [
                            "Дата регистрации",
                            "Имя", 
                            "Фамилия", 
                            "Email", 
                            "Место работы/учебы",
                            "Telegram ID",
                            "Username"
                        ]
                        worksheet.clear()  # Очищаем лист
                        worksheet.insert_row(headers, 1)
                        logger.info(f"Обновлены заголовки в листе {sheet_name}")
                    elif len(first_row) == 6:  # Старый формат без Username
                        # Добавляем колонку Username
                        worksheet.update_cell(1, 7, "Username")
                        logger.info(f"Добавлена колонка Username в лист {sheet_name}")
                except Exception as header_error:
                    logger.warning(f"Не удалось проверить заголовки для {sheet_name}: {header_error}")
                
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
                    "Telegram ID",
                    "Username"
                ]
                worksheet.append_row(headers)
                logger.info(f"Лист {sheet_name} создан с заголовками")
                
                return worksheet
                
        except Exception as e:
            logger.error(f"Ошибка при работе с листом {sheet_name}: {e}")
            raise
    
    def add_user_to_general_sheet(self, user: User) -> bool:
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
                str(user.telegram_id),
                user.username or ""  # Username может быть None
            ]
            
            worksheet.append_row(row_data)
            logger.info(f"Пользователь {user.first_name} {user.last_name} добавлен в общий лист")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя в общий лист: {e}")
            return False
    
    def add_user_to_event_sheet(self, user: User, event_name: str, sheet_name: str) -> bool:
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
                str(user.telegram_id),
                user.username or ""  # Username может быть None
            ]
            
            worksheet.append_row(row_data)
            logger.info(f"Пользователь {user.first_name} {user.last_name} добавлен на лист мероприятия {event_name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя на лист мероприятия {event_name}: {e}")
            return False
    
    def remove_user_from_event_sheet(self, user: User, sheet_name: str) -> bool:
        """Удалить пользователя с листа мероприятия."""
        try:
            worksheet = self._get_or_create_worksheet(sheet_name)
            
            # Получаем все значения таблицы
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:  # Только заголовки или пустая таблица
                logger.warning(f"Лист {sheet_name} пуст или содержит только заголовки")
                return False
            
            # Ищем строку с пользователем по Telegram ID
            telegram_id_str = str(user.telegram_id)
            user_row_index = None
            
            # Определяем индекс колонки Telegram ID
            headers = all_values[0] if all_values else []
            telegram_id_col = None
            
            for col_idx, header in enumerate(headers):
                if "Telegram ID" in str(header):
                    telegram_id_col = col_idx
                    break
            
            if telegram_id_col is None:
                logger.error(f"Колонка 'Telegram ID' не найдена в листе {sheet_name}")
                return False
            
            # Ищем пользователя по строкам (начиная с 1, пропускаем заголовки)
            for row_idx in range(1, len(all_values)):
                row = all_values[row_idx]
                if len(row) > telegram_id_col and str(row[telegram_id_col]) == telegram_id_str:
                    user_row_index = row_idx + 1  # +1 для корректного индекса в Google Sheets
                    break
            
            if user_row_index is None:
                logger.warning(f"Пользователь с Telegram ID {telegram_id_str} не найден на листе {sheet_name}")
                return False
            
            # Удаляем строку
            worksheet.delete_rows(user_row_index)
            logger.info(f"Пользователь {user.first_name} {user.last_name} (ID: {telegram_id_str}) удален с листа {sheet_name} (строка {user_row_index})")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления пользователя с листа мероприятия: {e}")
            return False