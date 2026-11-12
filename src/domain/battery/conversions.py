"""Строгие преобразования входных значений аккумулятора."""

from decimal import Decimal, InvalidOperation

_SCALAR_TYPES = (str, int, float, Decimal)
_STOCK_MARKERS = ('>', '<', 'более')


def text(raw: object) -> str | None:
    """Нормализовать пробелы, сохраняя ведущие нули строковых кодов."""
    if raw is None:
        return None
    if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
        raise ValueError('требуется текст или число')
    if isinstance(raw, (float, Decimal)):
        numeric = number(raw)
        if numeric is not None and numeric == numeric.to_integral_value():
            return str(int(numeric))
    return ' '.join(str(raw).split()) or None


def number(raw: object) -> Decimal | None:
    """Прочитать десятичное число без потери точности денежных значений."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    if isinstance(raw, bool) or not isinstance(raw, _SCALAR_TYPES):
        raise ValueError('требуется число')
    prepared = ''.join(str(raw).split()).replace(',', '.')
    try:
        numeric = Decimal(prepared)
    except InvalidOperation as exc:
        raise ValueError('требуется число') from exc
    if not numeric.is_finite():
        raise ValueError('требуется конечное число')
    return numeric


def integer(raw: object) -> int | None:
    """Целое без молчаливого округления дробной части."""
    numeric = number(raw)
    if numeric is None:
        return None
    if numeric != numeric.to_integral_value():
        raise ValueError('требуется целое число')
    return int(numeric)


def stock(raw: object) -> int | None:
    """Пороговые остатки приводятся как у шин: >30 и более 30 становятся 30."""
    if isinstance(raw, str):
        raw = raw.lower()
        for marker in _STOCK_MARKERS:
            raw = raw.replace(marker, '')
    return integer(raw)


def flag(raw: object) -> bool | None:
    """Не путать текстовое «нет» с True, а пустую ячейку с False."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        normalized = raw.strip().casefold()
        if normalized in {'да', 'нет'}:
            return normalized == 'да'
    raise ValueError('требуется да/нет или bool')
