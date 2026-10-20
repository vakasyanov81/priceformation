"""Исправление кириллических двойников в одной части слова (между разделителями)."""

from __future__ import annotations

from parsers.strategies.homoglyph_alphabet import (
    CYRILLIC,
    DOUBLE_CYRILLIC,
    LATIN,
    convert,
    forced_alphabets,
    is_cyrillic,
    is_latin,
    letters_of,
)


def _target_alphabet(part: str) -> str | None:
    """Алфавит смешанной части или None, если определить нельзя."""
    letters = letters_of(part)
    forced = forced_alphabets(letters)
    if forced:
        return forced.pop() if len(forced) == 1 else None
    latin = sum(is_latin(char) for char in letters)
    cyrillic = len(letters) - latin
    if latin != cyrillic:
        return LATIN if latin > cyrillic else CYRILLIC
    return LATIN if any(char.isdigit() for char in part) else None


def is_mixed(part: str) -> bool:
    letters = letters_of(part)
    return any(map(is_latin, letters)) and any(map(is_cyrillic, letters))


def lone_double(part: str) -> bool:
    """Часть из одной буквы-двойника (`Р`, `Е3`): алфавит берётся у соседних частей."""
    letters = letters_of(part)
    return len(letters) == 1 and letters[0] in DOUBLE_CYRILLIC


def fix_part(part: str, *, latin_sibling: bool) -> tuple[str, bool]:
    """Исправить одну часть слова; True во втором элементе — смесь алфавитов определить не удалось."""
    if is_mixed(part):
        target = _target_alphabet(part)
        return (convert(part, target), False) if target else (part, True)
    if latin_sibling and lone_double(part):
        return convert(part, LATIN), False
    return part, False


def is_latin_part(part: str) -> bool:
    """Часть с латинскими буквами и без кириллических."""
    return bool(letters_of(part)) and not any(map(is_cyrillic, part))
