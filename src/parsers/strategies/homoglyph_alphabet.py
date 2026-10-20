"""Алфавиты и таблицы кириллических двойников: общие примитивы для разбора токенов."""

from __future__ import annotations

from typing import Final

from parsers.strategies.normalize import CYRILLIC_HOMOGLYPHS, LATIN_HOMOGLYPHS

LATIN: Final = 'lat'
CYRILLIC: Final = 'cyr'
# Строчные в, н, т, к, м на латиницу не похожи: в смешанной части их двойниками не считаем.
_NOT_SIMILAR_LOWER: Final = 'внткм'
_PAIRS: Final = [
    pair for pair in zip(CYRILLIC_HOMOGLYPHS, LATIN_HOMOGLYPHS, strict=True) if pair[0] not in _NOT_SIMILAR_LOWER
] + [('у', 'y')]
_TO_LATIN: Final = str.maketrans(dict(_PAIRS))
_TO_CYRILLIC: Final = str.maketrans({lat: cyr for cyr, lat in _PAIRS})
DOUBLE_CYRILLIC: Final = frozenset(cyr for cyr, _ in _PAIRS)
DOUBLE_LATIN: Final = frozenset(lat for _, lat in _PAIRS)
_YO: Final = 'ё'


def is_cyrillic(char: str) -> bool:
    """Буква русского алфавита."""
    return 'а' <= char.lower() <= 'я' or char.lower() == _YO


def is_latin(char: str) -> bool:
    """Буква латинского алфавита."""
    return 'a' <= char.lower() <= 'z'


def letters_of(text: str) -> list[str]:
    """Только буквы (латиница и кириллица) в порядке следования."""
    return [char for char in text if is_cyrillic(char) or is_latin(char)]


def convert(text: str, target: str) -> str:
    """Заменить двойники на буквы целевого алфавита."""
    return text.translate(_TO_LATIN if target == LATIN else _TO_CYRILLIC)


def forced_alphabets(letters: list[str]) -> set[str]:
    """Алфавиты, подтверждённые буквами без двойника (`v`, `z`, `и`)."""
    forced: set[str] = set()
    for char in letters:
        if is_latin(char) and char not in DOUBLE_LATIN:
            forced.add(LATIN)
        if is_cyrillic(char) and char not in DOUBLE_CYRILLIC:
            forced.add(CYRILLIC)
    return forced
