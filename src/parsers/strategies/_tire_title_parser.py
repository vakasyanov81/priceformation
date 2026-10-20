# flake8: noqa: WPS202
"""Разбор и сборка названия шины (Пошк, STK, Пионер).

Пошк и STK пишут параметры шины вперемешку: ``н.с.N`` вместо ``NPR``, индекс
нагрузки/скорости стоит то до модели, то после неё, а производитель
(``НКШЗ``/``БШК``/``ОШЗ``/``ЯШЗ``/``ВолШЗ``) спрятан в хвосте названия,
а ``PR`` слипается с размером (``7.00 R16LT14PR``) или отрывается от числа
(``8 PR``). Разбираем название на параметры и собираем заново в каноническом порядке
(``nomenclature_title.TireTitleTokens``): ``размер бренд модель нагрузка/скорость PR камера ось``.
Из назначения в название идёт только ось из словаря (``Рулевая``/``Ведущая``/…), прочее (шип, завод,
``об/л``, ``спецшина``) в название не входит.

Примеры склейки → Пионер:

- ``10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт``
  → ``10.00R20 DOUBLEROAD DR-801 149/146K 18PR Универсальная``
- ``11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, (1 шт)``
  → ``11R22.5 TAITONG HS103 146/143M 16PR Ведущая``
- ``а/п 425/85R21 NORTEC TR-184-1 18PR 156J TT, шт``
  → ``425/85R21 NORTEC TR-184-1 156J 18PR TT``
- ``11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт``
  → ``11.00R20 НКШЗ И-68А 150/146K 16PR`` — производитель из хвоста
  становится брендом (``НКШЗ → Кама`` подставит ``ManufacturerFinder``)
- ``12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт``
  → ``12.4L-16 БШК Бел-160М 111A6 8PR``
- ``17.5-25 Rockbuster H108A E3/L3 н.с.28 спецшина, шт``
  → ``17.5-25 Rockbuster H108A E3/L3 28PR``
- ``Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал`` (STK)
  → ``235/75R17.5 LingLong LLA78 143/141J 18PR TL``
- ``Автошина 7.00 R16LT14PR 118/114L GREENSTONE ST896 змейка`` (STK)
  → ``7.00R16LT GREENSTONE ST896 118/114L 14PR``
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import NamedTuple

from domain.row_item.row_item import RowItem
from parsers.nomenclature_title import TireTitleTokens
from parsers.strategies._title_wins import TIRE_TITLE_WINS

_LEADING_KIND = re.compile(r'^\s*(?:а/п|автошина|автошины|автопокрышка)\b\.?\s*', re.IGNORECASE)
# Камера и ободная лента — не шина, их размер разбирает `_tube_title_parser`.
TUBE_PREFIX = re.compile(r'^\s*(?:авто)?камера\b|^\s*(?:ободная\s+)?лента\b', re.IGNORECASE)
_LEADING_SHIP = re.compile(r'^\s*Шина\b\s*', re.IGNORECASE)
_LAYER_SOURCE = re.compile(r'н\.\s*с\.?\s*(\d+)', re.IGNORECASE)
_SPLIT_PR = re.compile(r'(?<!\S)(\d+)\s+PR(?![^\s,])', re.IGNORECASE)
_TRAILING_PIECE = re.compile(r'\s*,?\s*,?\s*\(?\d*\s*шт\)?\s*$', re.IGNORECASE)
# Суффикс C/LT — только отдельной буквой: иначе `R16 Cordiant` дал бы `R16C ordiant`.
_SIZE = re.compile(
    r'(?P<width>\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?)'
    r'\s*(?P<lowpro>l)?\s*(?P<construct>[Rr]|[-–—])\s*'
    r'(?P<diameter>\d+(?:[.,]\d+)?)\s*(?:(?P<suffix>lt|[cс])(?![^\W\d_]))?',
    re.IGNORECASE,
)
# Дюймовый размер «внешний диаметр x ширина - посадочный»: `33x12.5-15`, `18x7-8`, `1220x400-533`.
_INCH_SIZE = re.compile(
    r'(?P<ext>\d+(?:[.,]\d+)?)\s*x\s*(?P<width>\d+(?:[.,]\d+)?)\s*-\s*'
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
# Альтернативная запись размера сразу за основным: `(1200x500-508)`, `/6.45-13`.
_ALT_SIZE = re.compile(r'^(?:\([^)]*\d[^)]*[x/\-][^)]*\)|/\d+(?:[.,]\d+)?-\d+(?:[.,]\d+)?)\s*')
_SIZE_SEPARATOR = re.compile(r'(?<=\d)\s*[хХ*]\s*(?=\d)')
_PR = re.compile(r'^\d+\s*PR$', re.IGNORECASE)
_LOAD_SPEED = re.compile(
    r'^(?P<load>(?:[4-9]\d|\d{3})(?:/\d{2,3})?)(?P<velocity>[A-Za-z]\d?)$',
)
_CAMERA = re.compile(r'^(?:TT|TL|TTF|TT/TL|TL/TT)$', re.IGNORECASE)
_KIND_WORDS = frozenset(('а/п', 'а/ш', 'автошина', 'автошины', 'автопокрышка'))
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
        '(карьер)',
        '(шашка)',
        '(волна)',
        '(клюшка)',
        'с',
        'трал',
        'шашка',
        'волна',
        'клюшка',
        'спецшина',
        'спецпокрышка',
        'сельхозшина',
        'сельхозпокрышка',
        'цельнолит',
        'змейка',
        'стройка',
        'кам',
        'зимняя',
    ),
)
# Начала токенов назначения: оси (`вед.ось`, `вед`, `руль/прицеп`, `приц.`, канонические `Универсальная`),
# индекс (`инд.102`), карьерный протектор (`карьер`, `карьерка/вед`).
_USAGE_PREFIXES = ('инд.', 'ось', 'вед', 'рул', 'унив', 'приц', 'карьер')
_DOT = '.'
# Заводской код без бренда: `ОИ-73Б`, `И-Н142Б`, `ВЛИ-10`, `Я-166`. До трёх заглавных букв —
# иначе под правило попали бы `КАМА-310` и `Алтайшина-421` (бренд со слитной моделью).
_FACTORY_CODE = re.compile(r'^[А-ЯЁ]{1,3}(?:-[А-ЯЁ])?-?\d+[А-ЯЁ]*$')
# Хвост, дописанный к обрезанной колонкой модели слитно: `A` в `AE-51A`, `+` в `NF201+`, `-1` в `Я-245-1`.
_MODEL_TAIL = re.compile(r'[\w+-]+')
# `R` в размере — радиальная конструкция, дефис и дюймовая запись — диагональная.
_CONSTRUCTIONS = {True: 'радиальная', False: 'диагональная'}
# Корень слова назначения → значение оси: `вед.ось`, `унив.ось`, `рулевая`, `приц.`, `руль/прицеп`.
_AXES = (
    ('вед', 'ведущая'),
    ('рул', 'рулевая'),
    ('унив', 'универсальная'),
    ('приц', 'прицепная'),
    ('карьер', 'карьерная'),
)
_TokenMatcher = Callable[[str], object]
_SPIKE_TOKENS = frozenset(('шип', 'шипы'))
_SPIKE_YES = 'Да'


class _SizeParts(NamedTuple):
    """Канонический размер и его части."""

    label: str
    width: str
    height_percent: str
    diameter: str
    ext_diameter: str = ''
    alt: str = ''
    construction: str = ''

    @classmethod
    def from_match(cls, match: re.Match[str], alt: str = '') -> _SizeParts:
        """Собрать канонический размер из совпадения регулярки; ``alt`` — размер в скобках."""
        diameter = match['diameter'].replace(',', _DOT)
        if 'ext' in match.re.groupindex:
            return cls._inch(match, diameter, alt)
        raw_width = match['width'].replace(',', _DOT)
        width, _, height = raw_width.partition('/')
        label = _size_label(width, height, diameter, match)
        return cls(label, width, height, diameter, '', alt, _CONSTRUCTIONS[match['construct'].upper() == 'R'])

    @classmethod
    def _inch(cls, match: re.Match[str], diameter: str, alt: str) -> _SizeParts:
        ext = match['ext'].replace(',', _DOT)
        width = match['width'].replace(',', _DOT)
        label = f'{ext}x{width}-{diameter}{(match["suffix"] or "").upper()}'
        return cls(label, width, '', diameter, ext, alt, _CONSTRUCTIONS[False])


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
class TireTitleParts:
    """Разобранные параметры названия Пошка/STK."""

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
        size: _SizeParts,
        tokens: list[str],
        from_ship: bool,
    ) -> TireTitleParts | None:
        """Собрать параметры из размера и остатка токенов; None без бренда с моделью."""
        service = _Service.from_tokens(tokens)
        fields = _resolve_fields(service.rest)
        if fields is None:
            return None
        return cls(
            size=size,
            brand=fields.brand,
            model=fields.model,
            load=service.load,
            velocity=service.velocity,
            layering=service.layering,
            intimacy=service.intimacy,
            usage=fields.usage,
            from_ship=from_ship,
        )

    @property
    def model_name(self) -> str:
        """Модель; у бренда со слитной моделью (``Кама-310``) — весь токен, он и есть название модели."""
        if self.model:
            return self.model
        return self.brand if any(char.isdigit() for char in self.brand) else ''

    def _size_with_alt(self) -> str:
        """Размер и альтернативная запись: ``/6.45-13`` клеится к размеру, ``(...)`` — через пробел."""
        glue = '' if self.size.alt.startswith('/') else ' '
        return f'{self.size.label}{glue}{self.size.alt}'.strip()

    def compose(self, brand: str | None = None) -> str:
        """Склеить название в каноническом порядке; brand перекрывает разобранный.

        Из назначения в название идёт только ось из словаря; остальные слова (шип, завод, ``об/л``)
        отдельные поля или шум.
        """
        return TireTitleTokens(
            self._size_with_alt(),
            _canonical_brand(self.brand, brand),
            self.model,
            load_velocity=f'{self.load}{self.velocity}',
            layering=self.layering,
            camera=self.intimacy,
            axis=_axis(self.usage),
        ).compose()


def _canonical_brand(parsed: str, canonical: str | None) -> str:
    """Канонический бренд вместо разобранного; приклеенную модель сохранить.

    ``GREENSTONE`` → ``GreenStone``, но ``Алтайшина-421``/``КАМА-310`` — бренд
    со слитной моделью: заменяется только начало, хвост ``-421`` остаётся.
    """
    if not canonical:
        return parsed
    if parsed.lower().startswith(canonical.lower()):
        return canonical + parsed[len(canonical) :]
    return canonical


def parse_tire_title(raw: str | None) -> TireTitleParts | None:
    """Разобрать название Пошка/STK на параметры; None, если это не размер шины."""
    if not raw or TUBE_PREFIX.match(raw):
        return None
    text = _prepare_text(raw)
    found = _find_size(text)
    if found is None:
        return None
    size_match, head, tail = found
    alt = _ALT_SIZE.match(tail)
    if alt is not None:
        tail = tail[alt.end() :]
    if not tail or tail[0] in '(/':
        return None
    size = _SizeParts.from_match(size_match, alt[0].strip() if alt else '')
    return TireTitleParts.from_raw(size, _clean_tokens(f'{head} {tail}'), _from_ship(raw))


def parse_leading_size(text: str) -> _SizeParts | None:
    """Размер в самом начале строки (дюймовый ``33x12.5-15`` или ``12.5/80-18``, ``215R16``); иначе None."""
    for pattern in (_INCH_SIZE, _SIZE):
        match = pattern.match(text)
        if match is not None:
            return _SizeParts.from_match(match)
    return None


def _find_size(text: str) -> tuple[re.Match[str], str, str] | None:
    """Размер, слова до него и остаток названия: сначала в начале строки, затем внутри."""
    for pattern in (_INCH_SIZE, _SIZE):
        match = pattern.match(text)
        if match is not None:
            return match, '', text[match.end() :].lstrip()
    inner = _INNER_SIZE.search(text)
    if inner is None or _OTHER_SIZE.search(text[: inner.start()]):
        return None
    return inner, text[: inner.start()].strip(), text[inner.end() :].lstrip()


def fill_tire_fields(row_item: RowItem, parts: TireTitleParts) -> None:
    """Записать разобранные параметры в поля позиции, не перетирая готовые."""
    fields = {
        'width': parts.size.width,
        'height_percent': parts.size.height_percent,
        'diameter': parts.size.diameter,
        'ext_diameter': parts.size.ext_diameter,
        'construction_type': parts.size.construction,
        'axis': _axis(parts.usage),
        'layering': parts.layering,
        'index_load': parts.load,
        'index_velocity': parts.velocity,
        'spike': _SPIKE_YES if any(token.lower().strip(_DOT) in _SPIKE_TOKENS for token in parts.usage) else '',
        'intimacy': parts.intimacy,
        'model': parts.model_name,
    }
    for key, parsed_value in fields.items():
        current = row_item.get_field(key)
        if parsed_value and (not current or _title_wins(key, current, parsed_value)):
            row_item.set_field(key, parsed_value)


def _title_wins(key: str, current: object, parsed: str) -> bool:
    """Значение из названия заменяет заполненное колонкой."""
    if key == 'model':
        return _completes_model(str(current), parsed)
    return key in TIRE_TITLE_WINS and _differs(current, parsed)


def _completes_model(column: str, parsed: str) -> bool:
    """Колонка обрезана: модель из названия — она же с приписанным слитно хвостом (`AE-51` → `AE-51A`)."""
    tail = parsed[len(column) :]
    return parsed.lower().startswith(column.lower()) and _MODEL_TAIL.fullmatch(tail) is not None


def _differs(current: object, parsed: str) -> bool:
    """Значения разные без учёта регистра: `да` из конфига и `Да` из названия — одно и то же."""
    return str(current).strip().lower() != parsed.lower()


def _axis(usage: tuple[str, ...]) -> str:
    """Ось из слов назначения; при нескольких (``рулевая/трал``) — по первому слову."""
    for token in usage:
        lower = token.lower()
        for root, axis in _AXES:
            if lower.startswith(root):
                return axis
    return ''


def _prepare_text(raw: str) -> str:
    """Срезать обёртки и привести ``н.с.N`` и разорванный ``N PR`` к ``NPR``."""
    text = _TRAILING_PIECE.sub('', raw.strip())
    text = _LEADING_KIND.sub('', text)
    text = _LEADING_SHIP.sub('', text)
    text = _LAYER_SOURCE.sub(r'\1PR', text)
    text = _SIZE_SEPARATOR.sub('x', text)
    return _SPLIT_PR.sub(r'\1PR', text)


def _clean_tokens(tail: str) -> list[str]:
    """Убрать запятые и слова-обёртки, обрезать суффиксы ``*шина``."""
    tokens = [token.strip(',') for token in tail.split()]
    return [_strip_kind_suffix(token) for token in tokens if token.lower() not in _KIND_WORDS]


def _strip_kind_suffix(token: str) -> str:
    """Срезать суффикс-обёртку: ``шип.автопокрышка`` → ``шип.``.

    Токен целиком из обёртки сюда не доходит — его отбрасывает ``_KIND_WORDS``.
    """
    lower = token.lower()
    for suffix in _KIND_SUFFIXES:
        if lower.endswith(suffix):
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
        return _without_producer(tokens)
    if _looks_like_brand(tokens[0]):
        fields = _compose_model(tokens[0], tokens[1:])
        return fields._replace(usage=(*fields.usage, producer))
    return _compose_model(producer, tokens)


def _without_producer(tokens: list[str]) -> _TitleFields | None:
    """Бренд и модель, когда завода в хвосте нет; None, если первое слово — назначение (``об/лента``)."""
    if _is_usage(tokens[0]):
        return None
    if _FACTORY_CODE.match(tokens[0]):
        return _compose_model('', tokens)
    return _compose_model(tokens[0], tokens[1:])


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
    return _LEADING_SHIP.match(raw) is not None


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
    construct = match['construct'].upper()
    profile = f'/{height}' if height else ''
    return f'{width}{profile}{lowpro}{construct}{diameter}{suffix}'
