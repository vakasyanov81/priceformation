"""Проверки числовых инвариантов аккумулятора без ввода-вывода."""

from decimal import Decimal


def check_number(numeric: Decimal | None, key: str, *, positive: bool = True) -> None:
    """Неизвестное допустимо; заданное число конечно и имеет допустимый знак."""
    if numeric is None:
        return
    if not isinstance(numeric, Decimal) or not numeric.is_finite():
        raise ValueError(f'{key}: требуется конечное десятичное число')
    if numeric < 0 or (positive and numeric == 0):
        raise ValueError(f'{key}: недопустимый знак числа')


def check_integer(numeric: int | None, key: str) -> None:
    """Количество и срок не могут быть дробными, отрицательными или bool."""
    if numeric is None:
        return
    if isinstance(numeric, bool) or not isinstance(numeric, int) or numeric < 0:
        raise ValueError(f'{key}: требуется неотрицательное целое число')


def check_flag(flag: bool | None, key: str) -> None:
    """Уже построенная модель не принимает строку вместо булевого признака."""
    if flag is not None and not isinstance(flag, bool):
        raise ValueError(f'{key}: требуется bool или None')
