"""Поиск согласованного разбиения слитных слов модели на пары раздельных."""

from collections.abc import Iterator


def _split_pairs(word: str, unmatched: frozenset[str]) -> Iterator[tuple[str, str]]:
    """Все пары разных слов, дающие `word` при склейке."""
    for first in unmatched:
        second = word.removeprefix(first)
        if second not in {word, first} and second in unmatched:
            yield first, second


def can_join(unmatched: frozenset[str], joined_words: tuple[str, ...]) -> bool:
    """Найти согласованные пары без повторного использования раздельных слов."""
    if not unmatched:
        return True
    if not joined_words:
        return False
    word, *remaining = joined_words
    rest = tuple(remaining)
    for pair in _split_pairs(word, unmatched):
        if can_join(unmatched.difference(pair), rest):
            return True
    return can_join(unmatched, rest)
