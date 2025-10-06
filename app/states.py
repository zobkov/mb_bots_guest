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
    events_list = State()
    confirm_registration = State()
    my_registrations = State()


class FaqSG(StatesGroup):
    """Состояния диалога поддержки."""
    faq = State()