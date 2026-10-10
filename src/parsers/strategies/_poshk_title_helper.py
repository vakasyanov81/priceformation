# flake8: noqa: WPS202
"""Разбор и сборка названия номенклатуры Пошка.

Пошк пишет параметры шины вперемешку: ``н.с.N`` вместо ``NPR``, индекс
нагрузки/скорости стоит то до модели, то после неё, а производитель
(``НКШЗ``/``БШК``/``ОШЗ``/``ЯШЗ``/``ВолШЗ``) спрятан в хвосте названия.
Разбираем название на параметры и собираем заново в порядке Пионера:
``размер бренд модель нагрузка/скорость PR камера назначение``.

Примеры склейки Пошк → Пионер:

- ``10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт``
  → ``10.00R20 DOUBLEROAD DR-801 149/146K 18PR унив.ось с об/л``
- ``11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, (1 шт)``
  → ``11R22.5 TAITONG HS103 146/143M 16PR вед.ось``
- ``а/п 425/85R21 NORTEC TR-184-1 18PR 156J TT, шт``
  → ``425/85R21 NORTEC TR-184-1 156J 18PR TT``
- ``11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт``
  → ``11.00R20 НКШЗ И-68А 150/146K 16PR`` — производитель из хвоста
  становится брендом (``НКШЗ → Кама`` подставит ``ManufacturerFinder``)
- ``12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт``
  → ``12.4L-16 БШК Бел-160М 111A6 8PR сельхозшина``
- ``17.5-25 Rockbuster H108A E3/L3 н.с.28 спецшина, шт``
  → ``17.5-25 Rockbuster H108A E3/L3 28PR спецшина``
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import NamedTuple

from domain.row_item.row_item import RowItem

_LEADING_KIND = re.compile(r'^\s*(?:а/п|автошина|автошины|автопокрышка)\b\.?\s*', re.IGNORECASE)
_LEADING_SHIP = re.compile(r'^\s*Шина\b\s*', re.IGNORECASE)
_LAYER_SOURCE = re.compile(r'н\.\s*с\.?\s*(\d+)', re.IGNORECASE)
_TRAILING_PIECE = re.compile(r'\s*,?\s*,?\s*\(?\d*\s*шт\)?\s*$', re.IGNORECASE)
_SIZE = re.compile(
    r'(?P<width>\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?)'
    r'\s*(?P<lowpro>l)?\s*(?P<construct>[Rr]|[-–—])\s*'
    r'(?P<diameter>\d+(?:[.,]\d+)?)\s*(?P<suffix>lt|[cс])?',
    re.IGNORECASE,
)
_PR = re.compile(r'^\d+\s*PR$', re.IGNORECASE)
_LOAD_SPEED = re.compile(
    r'^(?P<load>(?:[4-9]\d|\d{3})(?:/\d{2,3})?)(?P<velocity>[A-Za-z]\d?)$',
)
_CAMERA = re.compile(r'^(?:TT|TL|TTF|TT/TL|TL/TT)$', re.IGNORECASE)
_KIND_WORDS = frozenset(('а/п', 'автошина', 'автошины', 'автопокрышка'))
_KIND_SUFFIXES = ('автошина', 'автошины', 'автопокрышка')
_PRODUCERS = frozenset(('НКШЗ', 'БШК', 'ОШЗ', 'ЯШЗ', 'ВОЛШЗ'))
_USAGE_WORDS = frozenset(
    (
        'об/л',
        'об/лента',
        'шипы',
        'шип',
        'шип.',
        'б/к',
        'прицеп',
        'руль/прицеп',
        '(карьер)',
        '(шашка)',
        '(волна)',
        '(клюшка)',
        'с',
        'карьер',
        'трал',
        'шашка',
        'волна',
        'клюшка',
        'спецшина',
        'спецпокрышка',
        'сельхозшина',
        'цельнолит',
    ),
)
_USAGE_PREFIXES = ('инд.', 'ось', 'вед.', 'рул.', 'руль.', 'унив.', 'приц.', 'прицеп')
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


class _TitleFields(NamedTuple):
    """Бренд, модель и назначение, выделенные из остатка токенов."""

    brand: str
    model: str
    usage: tuple[str, ...]


class _Service(NamedTuple):
    """Служебные токены и остаток названия."""

    layering: str
    intimacy: str
    load: str
    velocity: str
    rest: tuple[str, ...]

    @classmethod
    def from_tokens(cls, tokens: list[str]) -> _Service:
        """Вырезать PR, камерность и индекс нагрузки/скорости из токенов."""
        layering, rest = _take_token(tokens, _PR.match)
        intimacy, rest = _take_token(rest, _CAMERA.match)
        load, velocity, rest = _take_speed(rest)
        return cls(layering.upper(), intimacy.upper(), load, velocity, tuple(rest))


@dataclass(frozen=True, slots=True)
class PoshkTitleParts:
    """Разобранные параметры названия Пошка."""

    size: _SizeParts
    brand: str
    model: str
    load: str
    velocity: str
    layering: str
    intimacy: str
    usage: tuple[str, ...]
    from_ship: bool = False

    @classmethod
    def from_raw(
        cls,
        size_match: re.Match[str],
        tokens: list[str],
        from_ship: bool,
    ) -> PoshkTitleParts | None:
        """Собрать параметры из размера и остатка токенов; None без бренда с моделью."""
        service = _Service.from_tokens(tokens)
        fields = _resolve_fields(service.rest)
        if fields is None:
            return None
        return cls(
            size=_SizeParts.from_match(size_match),
            brand=fields.brand,
            model=fields.model,
            load=service.load,
            velocity=service.velocity,
            layering=service.layering,
            intimacy=service.intimacy,
            usage=fields.usage,
            from_ship=from_ship,
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


def parse_poshk_title(raw: str) -> PoshkTitleParts | None:
    """Разобрать название Пошка на параметры; None, если это не размер шины."""
    text = _prepare_text(raw)
    size_match = _SIZE.match(text)
    if size_match is None:
        return None
    tail = text[size_match.end() :].lstrip()
    if not tail or tail[0] in '(/':
        return None
    return PoshkTitleParts.from_raw(size_match, _clean_tokens(tail), _from_ship(raw))


def fill_poshk_fields(row_item: RowItem, parts: PoshkTitleParts) -> None:
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


def _prepare_text(raw: str) -> str:
    """Срезать обёртки и привести ``н.с.N`` к ``NPR``."""
    text = _TRAILING_PIECE.sub('', (raw or '').strip())
    text = _LEADING_KIND.sub('', text)
    text = _LEADING_SHIP.sub('', text)
    return _LAYER_SOURCE.sub(r'\1PR', text)


def _clean_tokens(tail: str) -> list[str]:
    """Убрать запятые и слова-обёртки, склеить ``N PR`` и обрезать суффиксы ``*шина``."""
    tokens = [token.strip(',') for token in tail.split()]
    tokens = [token for token in tokens if token.lower() not in _KIND_WORDS]
    return [_strip_kind_suffix(token) for token in _merge_pr(tokens)]


def _merge_pr(tokens: list[str]) -> list[str]:
    """Склеить разорванный ``8 PR`` в ``8PR``."""
    merged: list[str] = []
    for token in tokens:
        previous = merged[-1] if merged else ''
        if token.upper() == 'PR' and previous.isdigit():
            merged[-1] = f'{previous}PR'
        else:
            merged.append(token)
    return merged


def _strip_kind_suffix(token: str) -> str:
    """Срезать суффикс-обёртку: ``шип.автопокрышка`` → ``шип.``."""
    lower = token.lower()
    for suffix in _KIND_SUFFIXES:
        if lower.endswith(suffix) and len(lower) > len(suffix):
            return token[: -len(suffix)]
    return token


def _resolve_fields(rest: tuple[str, ...]) -> _TitleFields | None:
    """Бренд, модель и назначение из остатка; None без бренда с моделью."""
    if not rest:
        return None
    producer, tokens = _take_token(list(rest), _is_producer)
    if not tokens:
        return None
    if not producer:
        return _compose_model(tokens[0], tokens[1:])
    if _looks_like_brand(tokens[0]):
        fields = _compose_model(tokens[0], tokens[1:])
        return fields._replace(usage=(*fields.usage, producer))
    return _compose_model(producer, tokens)


def _compose_model(brand: str, model_tokens: list[str]) -> _TitleFields:
    """Бренд, модель и назначение по токенам модели (назначение — от первого маркера)."""
    for index, token in enumerate(model_tokens):
        if _is_usage(token):
            model = model_tokens[:index]
            usage = tuple(model_tokens[index:])
            return _TitleFields(brand, ' '.join(model), usage)
    return _TitleFields(brand, ' '.join(model_tokens), ())


def _looks_like_brand(token: str) -> bool:
    """Первый токен похож на бренд: латиница (``Tyrex``) или «кама» (``КАМА-310``)."""
    has_latin = any(char.isascii() and char.isalpha() for char in token)
    return has_latin or 'кама' in token.lower()


def _is_producer(token: str) -> bool:
    """Токен — завод-производитель из хвоста названия."""
    return token.upper() in _PRODUCERS


def _is_usage(token: str) -> bool:
    """Токен назначения/особенности: об/л, оси, шипы, инд., карьер и т.п."""
    lower = token.lower()
    return lower in _USAGE_WORDS or lower.startswith(_USAGE_PREFIXES)


def _from_ship(raw: str) -> bool:
    """Название начиналось с обёртки «Шина» (нужно для бренд-заглушки)."""
    return _LEADING_SHIP.match(raw or '') is not None


def _take_token(tokens: list[str], matches: _TokenMatcher) -> tuple[str, list[str]]:
    """Первый подходящий токен и список без него."""
    for index, token in enumerate(tokens):
        if matches(token):
            return token, tokens[:index] + tokens[index + 1 :]
    return '', tokens


def _take_speed(tokens: list[str]) -> tuple[str, str, list[str]]:
    """Индекс нагрузки/скорости и остаток токенов: ``149/146K``, ``111A6``."""
    speed, rest = _take_token(tokens, _LOAD_SPEED.match)
    match = _LOAD_SPEED.match(speed)
    if match is None:
        return '', '', rest
    return match['load'], match['velocity'], rest


def _size_label(width: str, height: str, diameter: str, match: re.Match[str]) -> str:
    """Склеить размер: ``10.00R20``, ``12.4L-16``, ``425/85R21LT``."""
    lowpro = (match['lowpro'] or '').upper()
    suffix = (match['suffix'] or '').upper()
    construct = 'R' if match['construct'].upper() == 'R' else match['construct']
    profile = f'/{height}' if height else ''
    return f'{width}{profile}{lowpro}{construct}{diameter}{suffix}'
