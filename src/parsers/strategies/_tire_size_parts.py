"""Размер шины в названии: регулярки, канонический размер и его части."""

from __future__ import annotations

import re
from typing import NamedTuple

DOT = '.'
# Суффикс C/LT — только отдельной буквой: иначе `R16 Cordiant` дал бы `R16C ordiant`.
_SIZE = re.compile(
    r'(?P<width>\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?)'
    r'\s*(?P<lowpro>l)?\s*(?P<construct>[Rr]|[-–—])\s*'
    r'(?P<diameter>\d+(?:[.,]\d+)?)\s*(?:(?P<suffix>lt|[cс])(?![^\W\d_]))?',
    re.IGNORECASE,
)
# Дюймовый размер «внешний диаметр x ширина - посадочный»: `33x12.5-15`, `18x7-8`, `1220x400-533`;
# у радиальной вместо дефиса `R`: `31X10.50R15LT`.
_INCH_SIZE = re.compile(
    r'(?P<ext>\d+(?:[.,]\d+)?)\s*x\s*(?P<width>\d+(?:[.,]\d+)?)\s*(?P<construct>[R-])\s*'
    r'(?P<diameter>\d+(?:[.,]\d+)?)\s*(?:(?P<suffix>lt|[cс])(?![^\W\d_]))?',
    re.IGNORECASE,
)
# Размер не в начале строки ищем только по радиальному написанию: иначе поймаем модель вроде `153`.
_INNER_SIZE = re.compile(
    r'(?<!\S)(?P<width>\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?)\s*(?P<lowpro>l)?\s*(?P<construct>R)\s*'
    r'(?P<diameter>\d+(?:[.,]\d+)?)\s*(?:(?P<suffix>lt|[cс])(?![^\W\d_]))?',
)
# Другой размер перед найденным: тогда основной размер — не он.
_OTHER_SIZE = re.compile(r'\d\s*[x/\-]\s*\d')
# Лишний ноль у дробной ширины: `10.50` → `10.5`, `7.50` → `7.5`; `13.0` остаётся как в прайсе.
TRAILING_ZEROS = re.compile(r'^(\d+\.\d*[1-9])0+$')
# `R` в размере — радиальная конструкция, дефис и дюймовая запись — диагональная.
_CONSTRUCTIONS = {True: 'радиальная', False: 'диагональная'}


class SizeParts(NamedTuple):
    """Канонический размер и его части."""

    label: str
    width: str
    height_percent: str
    diameter: str
    ext_diameter: str = ''
    alt: str = ''
    construction: str = ''

    @classmethod
    def from_match(cls, match: re.Match[str], alt: str = '') -> SizeParts:
        """Собрать канонический размер из совпадения регулярки; ``alt`` — размер в скобках."""
        diameter = match['diameter'].replace(',', DOT)
        if 'ext' in match.re.groupindex:
            return cls._inch(match, diameter, alt)
        width, height = _split_width(match)
        label = size_label(width, height, diameter, match)
        return cls(label, width, height, diameter, '', alt, _CONSTRUCTIONS[_is_radial(match)])

    @classmethod
    def _inch(cls, match: re.Match[str], diameter: str, alt: str) -> SizeParts:
        ext = match['ext'].replace(',', DOT)
        width = match['width'].replace(',', DOT)
        label = inch_label(match, ext, width, diameter)
        return cls(label, width, '', diameter, ext, alt, _CONSTRUCTIONS[_is_radial(match)])


def _split_width(match: re.Match[str]) -> tuple[str, str]:
    """Ширина и профиль из ``205/55``; без профиля — пустая строка."""
    raw = match['width'].replace(',', DOT)
    width, _, height = raw.partition('/')
    return width, height


def _is_radial(match: re.Match[str]) -> bool:
    """Конструкция в размере — ``R`` (радиальная), а не дефис."""
    return match['construct'].upper() == 'R'


def size_label(width: str, height: str, diameter: str, match: re.Match[str]) -> str:
    """Склеить размер: ``10.00R20``, ``12.4L-16``, ``425/85R21LT``."""
    lowpro = (match['lowpro'] or '').upper()
    suffix = (match['suffix'] or '').upper()
    construct = match['construct'].upper()
    profile = f'/{height}' if height else ''
    return f'{width}{profile}{lowpro}{construct}{diameter}{suffix}'


def inch_label(match: re.Match[str], ext: str, width: str, diameter: str) -> str:
    """Склеить дюймовый размер: ``33x12.5-15``, ``31x10.5R15LT``; у радиальной лишний ноль ширины срезается."""
    construct = match['construct'].upper()
    suffix = (match['suffix'] or '').upper()
    label_width = TRAILING_ZEROS.sub(r'\1', width) if construct == 'R' else width
    return f'{ext}x{label_width}{construct}{diameter}{suffix}'


def parse_leading_size(text: str) -> SizeParts | None:
    """Размер в самом начале строки (дюймовый ``33x12.5-15`` или ``12.5/80-18``, ``215R16``); иначе None."""
    for pattern in (_INCH_SIZE, _SIZE):
        match = pattern.match(text)
        if match is not None:
            return SizeParts.from_match(match)
    return None


def find_size(text: str) -> tuple[re.Match[str], str, str] | None:
    """Размер, слова до него и остаток названия: сначала в начале строки, затем внутри."""
    for pattern in (_INCH_SIZE, _SIZE):
        match = pattern.match(text)
        if match is not None:
            return match, '', text[match.end() :].lstrip()
    inner = _INNER_SIZE.search(text)
    if inner is None:
        return None
    before = text[: inner.start()]
    if _OTHER_SIZE.search(before):
        return None
    return inner, before.strip(), text[inner.end() :].lstrip()
