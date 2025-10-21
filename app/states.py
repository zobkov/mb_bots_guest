"""Состояния диалогов."""
from aiogram.fsm.state import State, StatesGroup


class StartSG(StatesGroup):
    """Состояния диалога регистрации."""
    welcome = State()
    first_name = State()
    last_name = State()
    email = State()
    workplace = State()
    confirmation = State()


class MainMenuSG(StatesGroup):
    """Состояния главного меню."""
    menu = State()


class RegistrationSG(StatesGroup):
    """Состояния диалога регистрации на мероприятия."""
    optional_events = State()      # Выбор мероприятий
    confirm_registration = State() # Подтверждение выбора
    my_registrations = State()     # Просмотр текущих регистраций


class FaqSG(StatesGroup):
    """Состояния диалога поддержки."""
    faq = State()


class ReferralSG(StatesGroup):
    """Состояния диалога реферальной программы."""
    dashboard = State()


class PassportSG(StatesGroup):
    """Состояния диалога паспортных данных."""
    instructions = State()
    passport_info = State()  # legacy совместимость
    full_name = State()
    passport_number = State()
    car_number = State()