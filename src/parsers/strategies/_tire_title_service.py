"""Служебные токены названия шины: PR, камерность, индексы, `XL`, `M+S`/`3PMSF`."""

from __future__ import annotations

import re
from typing import NamedTuple

from parsers.nomenclature_labels import season_marks_label, xl_label
from parsers.strategies._tire_title_tokens import TokenMatcher, take_speed, take_token

_PR = re.compile(r'^\d+\s*PR$', re.IGNORECASE)
_CAMERA = re.compile(r'^(?:TT|TL|TTF|TT/TL|TL/TT)$', re.IGNORECASE)
# Метка `XL` и сезонные метки `M+S`/`3PMSF`.
Properties = tuple[str, tuple[str, ...]]


class Service(NamedTuple):
    """Служебные токены и остаток названия."""

    layering: str
    intimacy: str
    load: str
    velocity: str
    xl: str
    season_marks: tuple[str, ...]
    rest: tuple[str, ...]

    @classmethod
    def from_tokens(cls, tokens: list[str]) -> Service:
        """Вырезать PR, камерность, индекс нагрузки/скорости, `XL` и `M+S`/`3PMSF` из токенов."""
        layering, rest = _take_upper(tokens, _PR.match)
        intimacy, rest = _take_upper(rest, _CAMERA.match)
        speed, rest = take_speed(rest)
        properties, rest = _split_properties(rest)
        return cls(layering, intimacy, *speed, *properties, tuple(rest))


def _take_upper(tokens: list[str], matches: TokenMatcher) -> tuple[str, list[str]]:
    """Первый подходящий токен в верхнем регистре и список без него."""
    token, rest = take_token(tokens, matches)
    return token.upper(), rest


def _split_properties(tokens: list[str]) -> tuple[Properties, list[str]]:
    """`XL` и сезонные метки из токенов-свойств и остаток токенов без них."""
    marks = [token for token in tokens if _is_property_token(token)]
    rest = [token for token in tokens if not _is_property_token(token)]
    text = ' '.join(marks)
    return (xl_label(text), season_marks_label(text)), rest


def _is_property_token(token: str) -> bool:
    """Отдельный токен `XL`, `M+S` или `3PMSF`: свойство шины, а не часть модели."""
    return bool(xl_label(token) or season_marks_label(token))
