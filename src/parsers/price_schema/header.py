"""Заголовок колонки прайса по строкам шапки."""

from collections.abc import Iterator

from parsers.price_schema.models import HeadRows


def column_header(rows: HeadRows, column: int) -> str:
    """Заголовок колонки — самый нижний непустой текст над строкой данных."""
    return next(_column_texts(rows, column), '')


def _column_texts(rows: HeadRows, column: int) -> Iterator[str]:
    """Тексты колонки снизу вверх, нормализованные по пробелам."""
    for row in reversed(rows):
        cell = row[column] if column < len(row) else None
        if isinstance(cell, str) and cell.strip():
            yield ' '.join(cell.split())
