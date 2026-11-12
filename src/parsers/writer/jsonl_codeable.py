"""Правила, какие значения jsonl можно заменить на @N."""


def is_codable_value(cell: object, code: str | None = None) -> bool:
    """Нечисловая строка; с кодом — только если @N короче значения."""
    if not isinstance(cell, str):
        return False
    try:
        float(cell)
    except ValueError:
        return code is None or len(code) < len(cell)
    return False
