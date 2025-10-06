"""Диалог регистрации пользователя (start)."""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Next
from aiogram_dialog.widgets.input import TextInput

from .handlers import (
    on_start_registration,
    on_first_name_entered,
    on_last_name_entered,
    on_email_entered,
    on_workplace_entered,
    on_restart_registration,
    on_confirm_registration
)
from .getters import get_user_data
from ...states import StartSG


def create_start_dialog() -> Dialog:
    """Создать диалог регистрации."""
    return Dialog(
        # Окно приветствия
        Window(
            Const(
                "<b>Привет!</b>\n"
                "Это форма регистрации на открытые мероприятия первого дня конференции\n"
                "<b>«Менеджмент Будущего '25»</b>\n\n"
                "Количество мест на каждое мероприятие ограничено, поэтому лучше не откладывать регистрацию.\n"
                "По любым вопросам можно обращаться на <b>program@mb-conference.ru</b>"
            ),
            Button(
                Const("🚀 Начать регистрацию"),
                id="start_registration",
                on_click=on_start_registration,
            ),
            state=StartSG.welcome,
        ),
        
        # Окно ввода имени
        Window(
            Const("<b>Введите ваше имя:</b>"),
            TextInput(
                id="first_name_input",
                on_success=on_first_name_entered,
            ),
            state=StartSG.first_name,
        ),
        
        # Окно ввода фамилии
        Window(
            Const("<b>Введите вашу фамилию:</b>"),
            TextInput(
                id="last_name_input",
                on_success=on_last_name_entered,
            ),
            state=StartSG.last_name,
        ),
        
        # Окно ввода email
        Window(
            Const("<b>Введите ваш адрес электронной почты:</b>"),
            TextInput(
                id="email_input",
                on_success=on_email_entered,
            ),
            state=StartSG.email,
        ),
        
        # Окно ввода места работы/учебы
        Window(
            Const("<b>Введите ваше текущее место работы/учёбы:</b>"),
            TextInput(
                id="workplace_input",
                on_success=on_workplace_entered,
            ),
            state=StartSG.workplace,
        ),
        
        # Окно подтверждения данных
        Window(
            Format(
                "<b>Проверьте введенные данные:</b>\n\n"
                "👤 <b>Имя:</b> {first_name}\n"
                "👤 <b>Фамилия:</b> {last_name}\n"
                "📧 <b>Email:</b> {email}\n"
                "🏢 <b>Место работы/учёбы:</b> {workplace}\n\n"
                "Всё верно?"
            ),
            Button(
                Const("❌ Заполнить заново"),
                id="restart",
                on_click=on_restart_registration,
            ),
            Button(
                Const("✅ Продолжить"),
                id="confirm",
                on_click=on_confirm_registration,
            ),
            getter=get_user_data,
            state=StartSG.confirmation,
        ),
    )