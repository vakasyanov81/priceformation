"""Поиск алиасов производителей в названии: границы слова и текст в скобках."""

import re


def _has_word_boundaries(title_lower: str, position: int, alias_len: int) -> bool:
    """Слева и справа от алиаса — не буква и не цифра."""
    before = title_lower[position - 1] if position > 0 else ''
    after_index = position + alias_len
    after = title_lower[after_index] if after_index < len(title_lower) else ''
    return not (before.isalnum() or after.isalnum())


def find_bounded(title_lower: str, lower_alias: str) -> int:
    """Найти алиас как отдельное слово: границы — не буква и не цифра.

    Раньше алиас искался только между пробелами/на краях title, поэтому
    бренды, склеенные с дефисом или скобками (``NORTEC-16``, ``АЛТАЙШИНА-111``),
    не находились, хотя есть в списке производителей.
    """
    if not title_lower or not lower_alias:
        return -1
    alias_len = len(lower_alias)
    position = title_lower.find(lower_alias)
    while position != -1:
        if _has_word_boundaries(title_lower, position, alias_len):
            return position
        position = title_lower.find(lower_alias, position + 1)
    return -1


_BRACKETS = re.compile(r'\([^)]*\)')


def blank_brackets(title: str) -> str:
    """Название с текстом в скобках, заменённым пробелами той же длины (позиции совпадений не сдвигаются).

    В скобках поставщик пишет владельца бренда (`Gislaved (Bridgestone)`): производитель позиции — слово перед ними.
    """
    return _BRACKETS.sub(lambda match: ' ' * len(match.group()), title)


def haystacks(title: str | None) -> tuple[str | None, ...]:
    """Где искать производителя: сначала вне скобок, затем и в них (завод — единственное упоминание бренда)."""
    if not title or '(' not in title:
        return (title,)
    return blank_brackets(title), title


def find_bracket_alias(
    title: str | None,
    bracket_aliases: tuple[str, ...],
    correct_by_alias: dict[str, str],
) -> tuple[str, str] | None:
    """Алиас, в имени которого есть скобки (`Ikon (Nokian Tyres)`): целиком это и есть производитель."""
    if not title or '(' not in title:
        return None
    lower = title.lower()
    for alias in bracket_aliases:
        position = find_bounded(lower, alias)
        if position != -1:
            return correct_by_alias[alias], title[position : position + len(alias)]
    return None
