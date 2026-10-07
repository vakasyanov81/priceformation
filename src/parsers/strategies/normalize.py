"""Стратегии нормализации исходного названия строки."""

from __future__ import annotations

import re

from domain.row_item.row_item import RowItem

_COMMA_IN_NUMBER = re.compile(r'(\d),(\d)')


class NormalizeTitle:
    """Схлопнуть пробелы и привести десятичную запятую к точке (``12,5`` → ``12.5``)."""

    def prepare(self, row_item: RowItem) -> str | None:
        """Исходный title с нормализацией пробелов и десятичных запятых."""
        title = row_item.identity.title
        if title is None:
            return None
        chunks = [chunk.strip() for chunk in title.split() if chunk.strip()]
        return _COMMA_IN_NUMBER.sub(r'\1.\2', ' '.join(chunks))
