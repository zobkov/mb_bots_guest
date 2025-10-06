"""Утилиты для диалога регистрации."""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Валидация email адреса."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_name(name: str, min_length: int = 2) -> Optional[str]:
    """
    Валидация имени/фамилии.
    Возвращает None если валидация прошла успешно, иначе текст ошибки.
    """
    name = name.strip()
    
    if not name:
        return "Поле не может быть пустым"
    
    if len(name) < min_length:
        return f"Должно содержать минимум {min_length} символа"
    
    if len(name) > 100:
        return "Слишком длинное значение (максимум 100 символов)"
    
    return None


def validate_workplace(workplace: str) -> Optional[str]:
    """
    Валидация места работы/учебы.
    Возвращает None если валидация прошла успешно, иначе текст ошибки.
    """
    workplace = workplace.strip()
    
    if not workplace:
        return "Место работы/учёбы не может быть пустым"
    
    if len(workplace) < 2:
        return "Должно содержать минимум 2 символа"
    
    if len(workplace) > 500:
        return "Слишком длинное значение (максимум 500 символов)"
    
    return None