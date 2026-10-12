"""Нормализация названия строки: стратегия слота `title` и функции разбора.

`NormalizeTitle` — стратегия слота `title`. Функции `normalize_text` и
`replace_homoglyphs` — чистая нормализация для независимого классификатора
типа товара (`product_type.py`): регистр, неразрывный пробел, десятичные
запятые и гомоглифы (кириллические С/Р/Х/М/Е/О/А/В/Т/Н/К → латиница).
"""

from __future__ import annotations

import re

from domain.row_item.row_item import RowItem

_COMMA_IN_NUMBER = re.compile(r'(\d),(\d)')
_WHITESPACE = re.compile(r'\s+')
_NBSP = '\xa0'

_CYRILLIC_HOMOGLYPHS = 'СРХМЕОАВТНКсрхмеоавтнк'
_LATIN_HOMOGLYPHS = 'CPXMEOABTHKcpxmeoabthk'
_HOMOGLYPHS = str.maketrans(_CYRILLIC_HOMOGLYPHS, _LATIN_HOMOGLYPHS)


def replace_homoglyphs(raw: str) -> str:
    """Заменить кириллические гомоглифы на визуально совпадающие латинские буквы."""
    return raw.translate(_HOMOGLYPHS)


def normalize_text(raw: str | None) -> str:
    """Нижний регистр, `\\xa0` → пробел, десятичная запятая → точка, одиночные пробелы.

    Гомоглифы здесь не трогаются: русские ключевые слова (`сельхоз`, `камер`…)
    должны оставаться читаемыми. Для технических токенов (размеры, суффиксы
    `C/LT/CP`, коды TRA) поверх результата накладывают `replace_homoglyphs`.
    """
    if not raw:
        return ''
    text = raw.replace(_NBSP, ' ')
    text = _COMMA_IN_NUMBER.sub(r'\1.\2', text)
    return _WHITESPACE.sub(' ', text).strip().lower()


class NormalizeTitle:
    """Схлопнуть пробелы и привести десятичную запятую к точке (``12,5`` → ``12.5``)."""

    def prepare(self, row_item: RowItem) -> str | None:
        """Исходный title с нормализацией пробелов и десятичных запятых."""
        title = row_item.identity.title
        if title is None:
            return None
        chunks = [chunk.strip() for chunk in title.split() if chunk.strip()]
        return _COMMA_IN_NUMBER.sub(r'\1.\2', ' '.join(chunks))
