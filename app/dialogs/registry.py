"""Инициализация всех диалогов."""
from aiogram import Router
from aiogram_dialog import setup_dialogs

from .start.dialogs import create_start_dialog
from .main_menu.dialogs import create_main_menu_dialog
from .registration.dialogs import create_registration_dialog
from .faq.dialogs import create_faq_dialog
from .referral.dialogs import create_referral_dialog
from .passport.dialogs import create_passport_dialog


def register_dialogs(router: Router) -> None:
    """Регистрация всех диалогов."""
    # Создаем диалоги
    start_dialog = create_start_dialog()
    main_menu_dialog = create_main_menu_dialog()
    registration_dialog = create_registration_dialog()
    faq_dialog = create_faq_dialog()
    referral_dialog = create_referral_dialog()
    passport_dialog = create_passport_dialog()
    
    # Регистрируем диалоги
    router.include_router(start_dialog)
    router.include_router(main_menu_dialog)
    router.include_router(registration_dialog)
    router.include_router(faq_dialog)
    router.include_router(referral_dialog)
    router.include_router(passport_dialog)
    
    # Настраиваем aiogram-dialog
    setup_dialogs(router)