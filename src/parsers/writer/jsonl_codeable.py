"""Правила, какие значения jsonl можно заменить на @N."""

from typing import Any


def is_codable_value(cell: object, code: str | None = None) -> bool:
    """Нечисловая строка; с кодом — только если @N короче значения."""
    if not isinstance(cell, str):
        return False
    try:
        float(cell)
    except ValueError:
        return code is None or len(code) < len(cell)
    return False


def usable_codes(existing: dict[str, Any]) -> dict[Any, str]:
    """Оставить в словаре только коды, которые имеют смысл хранить."""
    return {
        original_value: stored_code
        for stored_code, original_value in existing.items()
        if is_codable_value(original_value, stored_code)
    }
