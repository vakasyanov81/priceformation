"""Хвост названия шины после нагрузки+скорости: разбор по классам токенов и слияние признаков группы.

Классы по месту в каноническом порядке (``TireTitleTokens.compose``): прочее, ``XL``, ``<N>PR``, камерность,
``M+S``, ``3PMSF``, ``RunFlat``, ось. Из других названий группы в хвост эталона добавляются ``XL``, ``M+S``,
``3PMSF`` (их можно иметь вместе), а камерность и ось — только если у эталона их нет.
"""

import re
from collections.abc import Iterable
from itertools import chain, islice

from domain.row_item.row_item import RowItem
from parsers.nomenclature.labels import AXIS_NAMES, CAMERA_CODES
from parsers.nomenclature.title import load_velocity

_LAYERING = re.compile(r'\d+PR')
_FIXED_RANKS = {
    'XL': 1,
    **dict.fromkeys(CAMERA_CODES, 3),
    'M+S': 4,
    '3PMSF': 5,
    'RunFlat': 6,
    **dict.fromkeys(AXIS_NAMES, 7),
}
_LAYERING_RANK = 2
_SET_RANKS = frozenset((1, 4, 5))
_SINGLE_RANKS = frozenset((3, 7))

TitleSplit = tuple[list[str], list[str]]


def split_title(row_item: RowItem) -> TitleSplit | None:
    """Название шины: слова до нагрузки+скорости включительно и слова хвоста; нет такого токена — None."""
    words = (row_item.identity.title or '').split()
    end = _tail_start(words, load_velocity(row_item))
    if end is None:
        return None
    head = list(islice(words, end))
    return head, list(islice(words, end, None))


def _tail_start(words: list[str], load: str) -> int | None:
    """Позиция сразу после последнего слова нагрузки+скорости; такого слова нет — None."""
    positions = [position for position, word in enumerate(words) if word == load]
    if not load or not positions:
        return None
    return positions[-1] + 1


def merge_tails(reference: list[str], others: Iterable[list[str]]) -> list[str]:
    """Хвост эталона с признаками других названий группы в каноническом порядке."""
    merged = list(reference)
    taken = {_rank(word) for word in merged}
    for word in chain.from_iterable(others):
        rank = _rank(word)
        if _is_addable(rank, taken) and word not in merged:
            merged.append(word)
            taken.add(rank)
    return sorted(merged, key=_rank)


def _is_addable(rank: int, taken: set[int]) -> bool:
    return rank in _SET_RANKS or (rank in _SINGLE_RANKS and rank not in taken)


def _rank(word: str) -> int:
    """Место слова хвоста в каноническом порядке; незнакомые слова (0) остаются впереди."""
    if _LAYERING.fullmatch(word):
        return _LAYERING_RANK
    return _FIXED_RANKS.get(word, 0)
