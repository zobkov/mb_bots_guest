"""Репозиторий для работы с паспортными данными пользователей."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.passport import PassportData


class PassportRepository:
    """Репозиторий для CRUD-операций с паспортными данными."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Optional[PassportData]:
        """Вернуть паспортные данные пользователя, если они уже сохранены."""
        stmt = select(PassportData).where(PassportData.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_passport_data(
        self,
        user_id: int,
        full_name: str,
        passport_number: str,
        car_number: Optional[str] = None,
    ) -> PassportData:
        """Создать или обновить паспортные данные пользователя."""
        passport_data = await self.get_by_user_id(user_id)

        if passport_data is None:
            passport_data = PassportData(
                user_id=user_id,
                full_name=full_name,
                passport_number=passport_number,
                car_number=car_number,
            )
            self.session.add(passport_data)
        else:
            passport_data.full_name = full_name
            passport_data.passport_number = passport_number
            passport_data.car_number = car_number

        await self.session.flush()
        return passport_data
