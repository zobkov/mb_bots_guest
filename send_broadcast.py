"""Utility script for sending a broadcast message to users from CSV."""
import asyncio
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramRetryAfter

from app.config.config import load_config

CSV_PATH = Path("Регистрации гостей МБ25 - техвыгрузка.csv")
MESSAGE_TEXT = ("""Привет!
Программа открытых мероприятий обновлена – загляни в бота за новым расписанием."""
)

MENU_BUTTON_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Главное меню", callback_data="open_main_menu")]]
)


@dataclass
class Recipient:
    """Recipient info for the broadcast."""
    user_id: int
    username: str

    @property
    def display(self) -> str:
        """Return human readable representation for logging."""
        username_part = f"@{self.username}" if self.username else "(username не указан)"
        return f"{self.user_id} {username_part}"


def load_recipients(csv_path: Path) -> List[Recipient]:
    """Load recipients list from CSV file."""
    recipients: List[Recipient] = []
    if not csv_path.exists():
        raise FileNotFoundError(f"Файл {csv_path} не найден")

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            raw_id = (row.get("id") or "").strip()
            if not raw_id:
                continue

            try:
                user_id = int(raw_id)
            except ValueError:
                print(f"Пропускаю строку с некорректным id: {raw_id}")
                continue

            username = (row.get("Username") or row.get("username") or "").strip()
            recipients.append(Recipient(user_id=user_id, username=username))

    return recipients


def ask_for_confirmation(recipients: Iterable[Recipient], message: str) -> bool:
    """Print preview info and ask for confirmation."""
    recipients_list = list(recipients)

    print("\nСообщение для отправки:\n")
    print(message)
    print("\nПолучатели:")
    for recipient in recipients_list:
        print(f" - {recipient.display}")

    print(f"\nВсего получателей: {len(recipients_list)}")
    answer = input("\nОтправить сообщение? [y/N]: ").strip().lower()
    return answer in {"y", "yes", "д", "да"}


async def send_messages(bot: Bot, recipients: Iterable[Recipient], message: str) -> Tuple[List[int], List[Tuple[Recipient, str]]]:
    """Send messages to the provided recipients."""
    successes: List[int] = []
    failures: List[Tuple[Recipient, str]] = []

    for recipient in recipients:
        try:
            await bot.send_message(recipient.user_id, message, reply_markup=MENU_BUTTON_MARKUP)
            successes.append(recipient.user_id)
            await asyncio.sleep(0.2)
        except TelegramRetryAfter as exc:
            delay = int(exc.retry_after) + 1
            print(f"Телеграм просит подождать {delay} секунд перед отправкой пользователю {recipient.user_id}")
            await asyncio.sleep(delay)
            try:
                await bot.send_message(recipient.user_id, message, reply_markup=MENU_BUTTON_MARKUP)
                successes.append(recipient.user_id)
            except Exception as err:  # noqa: BLE001
                failures.append((recipient, str(err)))
        except Exception as err:  # noqa: BLE001
            failures.append((recipient, str(err)))
            await asyncio.sleep(0.5)

    return successes, failures


async def main() -> None:
    """Entry point for the broadcast script."""
    recipients = load_recipients(CSV_PATH)
    if not recipients:
        print("Список получателей пуст. Рассылка не запущена.")
        return

    if not ask_for_confirmation(recipients, MESSAGE_TEXT):
        print("Рассылка отменена пользователем.")
        return

    config = load_config()
    bot = Bot(token=config.bot.token)

    try:
        successes, failures = await send_messages(bot, recipients, MESSAGE_TEXT)
    finally:
        await bot.session.close()

    print(f"\nОтправлено успешно: {len(successes)}")
    if failures:
        print(f"Не удалось отправить: {len(failures)}")
        for recipient, error in failures:
            print(f" - {recipient.display}: {error}")
    else:
        print("Ошибок не обнаружено.")


if __name__ == "__main__":
    asyncio.run(main())
