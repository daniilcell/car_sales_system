"""
Вспомогательные функции
"""

import re
from typing import Optional


def format_price(price: float) -> str:
    """Форматирование цены в рублях"""
    return f"{price:,.0f} руб.".replace(",", " ")


def parse_price(price_str: str) -> Optional[float]:
    """Парсинг цены из строки"""
    try:
        cleaned = re.sub(r'[^\d.,]', '', price_str)
        cleaned = cleaned.replace(',', '.')
        return float(cleaned)
    except ValueError:
        return None


def validate_phone(phone: str) -> bool:
    """Валидация номера телефона"""
    cleaned = re.sub(r'[^\d+]', '', phone)
    return len(cleaned) >= 10


def validate_email(email: str) -> bool:
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_phone(phone: str) -> str:
    """Форматирование номера телефона"""
    cleaned = re.sub(r'[^\d]', '', phone)
    if len(cleaned) == 11 and cleaned[0] in '78':
        return f"+7 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:11]}"
    elif len(cleaned) == 10:
        return f"+7 ({cleaned[0:3]}) {cleaned[3:6]}-{cleaned[6:8]}-{cleaned[8:10]}"
    return phone


# Предустановленные данные
CAR_MODELS = [
    "WOW", "Lada Vesta", "Lada Granta", "Lada Niva", 
    "Haval Jolion", "Haval F7", "Chery Tiggo", "Geely Coolray",
    "EXEED TXL", "Omoda C5", "Changan CS55", "FAW Bestune T77"
]

CAR_COLORS = [
    "Белый", "Чёрный", "Серебристый", "Серый", "Красный", 
    "Синий", "Зелёный", "Коричневый", "Бежевый", "Оранжевый"
]

PAYMENT_METHODS = [
    "Наличные", "Банковский перевод", "Кредит", "Лизинг", "Trade-in"
]