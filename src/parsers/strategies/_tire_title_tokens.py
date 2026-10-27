"""Токены названия шины: срезать обёртки, разбить на слова, вынуть токен по признаку."""

from __future__ import annotations

import re
from collections.abc import Callable

_LEADING_KIND = re.compile(r'^\s*(?:а/п|автошина|автошины|автопокрышка)\b\.?\s*', re.IGNORECASE)
_LEADING_SHIP = re.compile(r'^\s*Шина\b\s*', re.IGNORECASE)
_LAYER_SOURCE = re.compile(r'н\.\s*с\.?\s*(\d+)', re.IGNORECASE)
_SPLIT_PR = re.compile(r'(?<!\S)(\d+)\s+PR(?![^\s,])', re.IGNORECASE)
_TRAILING_PIECE = re.compile(r'\s*,?\s*,?\s*\(?\d*\s*шт\)?\s*$', re.IGNORECASE)
_SIZE_SEPARATOR = re.compile(r'(?<=\d)\s*[хХ*]\s*(?=\d)')
_LOAD_SPEED = re.compile(
    r'^(?P<load>(?:[4-9]\d|\d{3})(?:/\d{2,3})?)(?P<velocity>[A-Za-z]\d?)$',
)
_KIND_WORDS = frozenset(('а/п', 'а/ш', 'автошина', 'автошины', 'автопокрышка'))
_KIND_SUFFIXES = ('автошина', 'автошины', 'автопокрышка')
TokenMatcher = Callable[[str], object]
# Индекс нагрузки и индекс скорости: ``('149/146', 'K')``.
LoadSpeed = tuple[str, str]


def prepare_text(raw: str) -> str:
    """Срезать обёртки и привести ``н.с.N`` и разорванный ``N PR`` к ``NPR``."""
    text = _TRAILING_PIECE.sub('', raw.strip())
    text = _LEADING_KIND.sub('', text)
    text = _LEADING_SHIP.sub('', text)
    text = _LAYER_SOURCE.sub(r'\1PR', text)
    text = _SIZE_SEPARATOR.sub('x', text)
    return _SPLIT_PR.sub(r'\1PR', text)


def clean_tokens(tail: str) -> list[str]:
    """Убрать запятые и слова-обёртки, обрезать суффиксы ``*шина``."""
    tokens = [token.strip(',') for token in tail.split()]
    return [_strip_kind_suffix(token) for token in tokens if token.lower() not in _KIND_WORDS]


def starts_with_ship(raw: str) -> bool:
    """Название начиналось с обёртки «Шина» (нужно для бренд-заглушки)."""
    return _LEADING_SHIP.match(raw) is not None


def take_token(tokens: list[str], matches: TokenMatcher) -> tuple[str, list[str]]:
    """Первый подходящий токен и список без него."""
    for index, token in enumerate(tokens):
        if matches(token):
            return token, tokens[:index] + tokens[index + 1 :]
    return '', tokens


def take_speed(tokens: list[str]) -> tuple[LoadSpeed, list[str]]:
    """Индекс нагрузки/скорости и остаток токенов: ``149/146K``, ``111A6``."""
    speed, rest = take_token(tokens, _LOAD_SPEED.match)
    match = _LOAD_SPEED.match(speed)
    if match is None:
        return ('', ''), rest
    return (match['load'], match['velocity']), rest


def _strip_kind_suffix(token: str) -> str:
    """Срезать суффикс-обёртку: ``шип.автопокрышка`` → ``шип.``.

    Токен целиком из обёртки сюда не доходит — его отбрасывает ``_KIND_WORDS``.
    """
    lower = token.lower()
    for suffix in _KIND_SUFFIXES:
        if lower.endswith(suffix):
            return token[: -len(suffix)]
    return token
