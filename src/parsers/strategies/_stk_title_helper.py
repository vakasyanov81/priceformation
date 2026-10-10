"""Разбор и сборка названия номенклатуры STK.

STK пишет параметры шины вперемешку: ``PR``, индекс нагрузки/скорости и
``TT/TL`` стоят то до бренда с моделью, то после, а ``PR`` слипается с
размером (``7.00 R16LT14PR``). Разбираем название на параметры и собираем
заново в порядке Пионера: ``размер бренд модель нагрузка/скорость PR камера
назначение``.

Примеры склейки STK → Пионер:

- ``Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка``
  → ``11R22.5 GREENSTONE DR668 146/143L 16PR шашка``
- ``Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал``
  → ``235/75R17.5 LingLong LLA78 143/141J 18PR TL трал``
- ``Автошина 12.00R24 DRC D931 20PR 160/157F TTF карьер``
  → ``12.00R24 DRC D931 160/157F 20PR TTF карьер``
- ``Автошина 7.00 R16LT14PR 118/114L GREENSTONE ST896 змейка``
  → ``7.00R16LT GREENSTONE ST896 118/114L 14PR змейка``
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import NamedTuple

from domain.row_item.row_item import RowItem

_LEADING_KIND = re.compile(r'^\s*(?:автошина|автошины)\b\.?\s*', re.IGNORECASE)
_SIZE = re.compile(
    r'(?P<width>\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?)'
    r'\s*(?P<construct>[Rr]|[-–—])\s*(?P<diameter>\d+(?:[.,]\d+)?)\s*(?P<suffix>LT|[CС])?',
    re.IGNORECASE,
)
_PR = re.compile(r'^\d+\s*PR$', re.IGNORECASE)
_LOAD_SPEED = re.compile(r'^\d{2,3}(?:/\d{2,3})?[A-Za-z]$')
_CAMERA = re.compile(r'^(?:TT|TL|TTF|TT/TL|TL/TT)$', re.IGNORECASE)
_DOT = '.'
_TokenMatcher = Callable[[str], object]


class _SizeParts(NamedTuple):
    """Канонический размер и его части."""

    label: str
    width: str
    height_percent: str
    diameter: str

    @classmethod
    def from_match(cls, match: re.Match[str]) -> _SizeParts:
        """Собрать канонический размер из совпадения регулярки."""
        raw_width = match['width'].replace(',', _DOT)
        width, _, height = raw_width.partition('/')
        diameter = match['diameter'].replace(',', _DOT)
        label = _size_label(width, height, diameter, match)
        return cls(label, width, height, diameter)


class _Marks(NamedTuple):
    """Служебные токены и остаток названия."""

    layering: str
    intimacy: str
    load: str
    velocity: str
    rest: tuple[str, ...]

    @classmethod
    def from_tokens(cls, tokens: list[str]) -> _Marks:
        """Вырезать PR, камерность и индекс нагрузки/скорости из токенов."""
        layering, rest = _take_token(tokens, _PR.match)
        intimacy, rest = _take_token(rest, _CAMERA.match)
        speed, rest = _take_token(rest, _LOAD_SPEED.match)
        return cls(
            layering.upper(),
            intimacy.upper(),
            speed[:-1],
            speed[-1:],
            tuple(rest),
        )


@dataclass(frozen=True, slots=True)
class StkTitleParts:
    """Разобранные параметры названия STK."""

    size: _SizeParts
    brand: str
    model: str
    load: str
    velocity: str
    layering: str
    intimacy: str
    usage: tuple[str, ...]

    @classmethod
    def from_raw(cls, size_match: re.Match[str], tokens: list[str]) -> StkTitleParts | None:
        """Собрать параметры из размера и остатка токенов; None без бренда."""
        marks = _Marks.from_tokens(tokens)
        if not marks.rest:
            return None
        rest = marks.rest
        brand = rest[0]
        model = rest[1] if len(rest) > 1 else ''
        return cls(
            size=_SizeParts.from_match(size_match),
            brand=brand,
            model=model,
            load=marks.load,
            velocity=marks.velocity,
            layering=marks.layering,
            intimacy=marks.intimacy,
            usage=marks.rest[2:],
        )

    def compose(self, brand: str | None = None) -> str:
        """Склеить название в порядке Пионера; brand перекрывает разобранный."""
        chunks = (
            self.size.label,
            brand or self.brand,
            self.model,
            f'{self.load}{self.velocity}',
            self.layering,
            self.intimacy,
            *self.usage,
        )
        return ' '.join(chunk for chunk in chunks if chunk)


def parse_stk_title(raw: str) -> StkTitleParts | None:
    """Разобрать название STK на параметры; None, если это не размер шины."""
    text = _LEADING_KIND.sub('', (raw or '').strip())
    size_match = _SIZE.match(text)
    if size_match is None:
        return None
    return StkTitleParts.from_raw(size_match, text[size_match.end() :].split())


def fill_stk_fields(row_item: RowItem, parts: StkTitleParts) -> None:
    """Записать разобранные параметры в поля позиции, не перетирая готовые."""
    model = '' if row_item.identity.model else parts.model
    fields = {
        'width': parts.size.width,
        'height_percent': parts.size.height_percent,
        'diameter': parts.size.diameter,
        'layering': parts.layering,
        'index_load': parts.load,
        'index_velocity': parts.velocity,
        'intimacy': parts.intimacy,
        'model': model,
    }
    for key, parsed_value in fields.items():
        if parsed_value and not row_item.get_field(key):
            row_item.set_field(key, parsed_value)


def _take_token(tokens: list[str], matches: _TokenMatcher) -> tuple[str, list[str]]:
    """Первый подходящий токен и список без него."""
    for index, token in enumerate(tokens):
        if matches(token):
            return token, tokens[:index] + tokens[index + 1 :]
    return '', tokens


def _size_label(width: str, height: str, diameter: str, match: re.Match[str]) -> str:
    """Склеить размер: ``235/75R17.5``, ``7.00R16LT``."""
    suffix = (match['suffix'] or '').upper()
    construct = 'R' if match['construct'].upper() == 'R' else match['construct']
    profile = f'/{height}' if height else ''
    return f'{width}{profile}{construct}{diameter}{suffix}'
