"""Сервис для работы с паспортными данными пользователей."""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.passport import PassportData
from app.database.models.user import User
from app.database.repositories.passport_repository import PassportRepository
from app.infrastructure.google_sheets.sheets_manager import GoogleSheetsManager


class PassportService:
    """Сервисный слой для сохранения и синхронизации паспортных данных."""

    def __init__(self, session: AsyncSession, sheets_manager: Optional[GoogleSheetsManager]):
        self._repository = PassportRepository(session)
        self._sheets_manager = sheets_manager

    async def get_user_passport_data(self, user_id: int) -> Optional[PassportData]:
        """Вернуть сохранённые паспортные данные пользователя."""
        return await self._repository.get_by_user_id(user_id)

    async def upsert_user_passport_data(
        self,
        user: User,
        full_name: str,
        passport_number: str,
        car_number: Optional[str] = None,
    ) -> PassportData:
        """Сохранить паспортные данные и синхронизировать их с Google Sheets."""
        prepared_full_name = " ".join(part.strip() for part in full_name.split() if part.strip())
        prepared_passport = passport_number.strip()
        prepared_car_number = car_number.strip() if car_number else None

        passport_data = await self._repository.upsert_passport_data(
            user_id=user.id,
            full_name=prepared_full_name,
            passport_number=prepared_passport,
            car_number=prepared_car_number,
        )

        # Синхронизация с листом "Пропуски" не является критичной, поэтому не бросаем исключение
        if self._sheets_manager:
            self._sheets_manager.upsert_passport_entry(
                user=user,
                full_name=passport_data.full_name,
                passport_number=passport_data.passport_number,
                car_number=passport_data.car_number,
            )

        return passport_data
