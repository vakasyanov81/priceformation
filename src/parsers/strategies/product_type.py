"""Независимый классификатор типа товара по названию и параметрам.

Правила — README.md, раздел «Определение типа товара»: нешинные позиции, форма
размера, спец-, мото-, грузовые, легкогрузовые и легковые шины. Категория здесь не
участвует (она сверяется отдельно, `product_types.declared_matches`).

Публичный интерфейс — `ProductTypeClassifier.classify(row_item) -> str`:
канонический тип или пустая строка, если тип не определён.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from domain.row_item.row_item import RowItem
from parsers.strategies.normalize import normalize_text, replace_homoglyphs
from parsers.strategies.product_types import (
    CAMERA,
    DISK,
    LIGHT_TRUCK,
    MOTO,
    O_RING,
    PASSENGER,
    RIM_TAPE,
    SPECIAL,
    TRUCK,
)

_SUFFIX = r'(?:\s*(c|lt|cp)\b)?'
_METRIC2 = re.compile(r'\b(\d{3})\s*/\s*(\d{2})\s*/\s*(\d{2}(?:\.\d)?)')
_METRIC = re.compile(rf'\b(\d{{3}})\s*/\s*(\d{{2,3}})\s*z?r?\s*-?\s*(\d{{2}}(?:\.\d)?){_SUFFIX}')
_INCH = re.compile(rf'(?<![\w.,])(\d{{1,2}}(?:\.\d{{1,2}})?)\s*z?r\s*(\d{{2}}(?:\.\d)?){_SUFFIX}')
_WIDTH_ONLY = re.compile(rf'\b(\d{{3}})\s*z?r\s*(\d{{2}}(?:\.\d)?){_SUFFIX}')
# Флотация `наружный_диаметр × ширина R/- посадочный` (`31x10.5R15`, `24x10-11`).
# Однозначный посадочный (`18*7-8`) сюда не попадает — это диагональ `7-8`.
_FLOTATION = re.compile(
    rf'\b(\d{{2,3}})\s*[*xх×]\s*(\d{{1,2}}(?:\.\d{{1,2}})?)\s*(?:-\s*|z?r\s*)(\d{{2}}(?:\.\d)?){_SUFFIX}',
)
_SLASH_DASH = re.compile(r'\b(\d{1,3}(?:\.\d{1,2})?)\s*/\s*(\d{1,3}(?:\.\d{1,2})?)\s*-\s*(\d{1,2}(?:\.\d)?)\b')
_AGRO_LR = re.compile(r'\b(\d{1,2}(?:\.\d)?)\s*l\s*r\s*(\d{2})\b')
_DASH = re.compile(r'\b(\d{1,2}(?:\.\d{1,2})?)\s*l?\s*-\s*(\d{1,2}(?:\.\d{1,2})?)\b')

_DOUBLE_LOAD = re.compile(r'\b(\d{2,3})\s*/\s*(\d{2,3})\b')
_AGRO_AI = re.compile(r'\b\d{2,3}\s*a[1-8]\b')
_PR_BEFORE = re.compile(r'\b(\d{1,2})\s*pr\b')
_PR_AFTER = re.compile(r'\bpr\s*(\d{1,2})\b')
_TRA = re.compile(r'\b(?:e3/l3|g2/l2|e4/l4|r-?4|r1|l5)\b')
_DISK_PAIR = re.compile(r'\d+(?:[.,]\d+)?\s*[*x]\s*\d+(?:[.,]\d+)?')
_DISK_PAIR_SLASH = re.compile(r'\d+(?:[.,]\d+)?\s*[*x]\s*\d+(?:[.,]\d+)?\s*/')
# Дюймовая ширина грузовой диагонали: две цифры от 10 и два знака (`11.00`, `12.00`).
_TRUCK_DASH_WIDTH = re.compile(r'[1-9]\d\.\d{2}')

_SPEC_WORDS = (
    'сельхоз',
    'спец',
    'индустр',
    'карьер',
    'клюшк',
    'волна',
    'шашк',
    'ёлк',
    'елк',
    'ромбик',
    'экскаватор',
    'погрузчик',
    'цельнолит',
    'solid',
    'трактор',
)
_MOTO_WORDS = ('мото', 'квадро', 'мотокарт', 'скутер')
_AXLE_WORDS = ('рул', 'вед', 'прицеп', 'трал', 'унив')
_COMMERCIAL_WORDS = ('van', 'vettore', 'effivan', 'tracvan', 'connex', 'cargo', 'lcv')
# Структурный маркер коммерческой шины в поле поставщика (`Тип авто` у mim).
_COMMERCIAL_MARKERS = frozenset(('c', 'lt', 'cp'))

_TRUCK_DIAMETERS = frozenset((17.5, 19.5, 22.5, 24.5))
_TRUCK_DIAMETER_MIN = 20
_TRUCK_DASH_DIAMETER_MIN = 17.5
_TRUCK_DASH_DIAMETER_MAX = 24
_TRUCK_PROFILE_HIGH = 80
_TRUCK_PROFILE_MIN = 65
_TRUCK_WIDTH_WIDE = 295
_AGRO_MIN_DIAMETER = 25
_AGRO_WIDE_DIAMETER = 24
_AGRO_WIDE_WIDTH = 340
_MOTO_MAX_WIDTH = 130
_MOTO_MAX_DIAMETER = 17
_MOTO_MIN_PROFILE = 70
_SUV_FLOTATION_RIM = 15
_TRUCK_PR = 14
_LOAD_INDEX_SCALE = 100


# Формы размера (README §4). Каждая хранит только то, что читают решения о
# семействе: ширина и диаметр из названия есть всегда, профиль — только у
# метрического размера и может быть неизвестен (размер из полей позиции).


@dataclass(frozen=True, slots=True)
class _Metric:
    """Метрический размер `205/55 R16`, `205/55/16` или из полей позиции."""

    width: float
    diameter: float
    profile: float | None = None
    commercial: bool = False


@dataclass(frozen=True, slots=True)
class _Inch:
    """Дюймовый/десятичный размер `7.50 R16`."""

    width: float
    diameter: float
    commercial: bool = False


@dataclass(frozen=True, slots=True)
class _Flotation:
    """Флотация `31x10.5R15`: решает посадочный диаметр."""

    diameter: float
    commercial: bool = False


@dataclass(frozen=True, slots=True)
class _WidthOnly:
    """Трёхзначная ширина без профиля `165 R13`: решают диаметр и PR."""

    diameter: float
    commercial: bool = False


@dataclass(frozen=True, slots=True)
class _Dash:
    """Диагональ `11.00-20`: грузовая или индустрия по исходной ширине и диаметру."""

    width_raw: str
    diameter: float


@dataclass(frozen=True, slots=True)
class _SpecialForm:
    """Форма, которая сама по себе означает спецшину: `16.9/14-30`, `9.5LR15`."""


type _TireSize = _Metric | _Inch | _Flotation | _WidthOnly | _Dash
type _Size = _TireSize | _SpecialForm


class ProductTypeClassifier:
    """Независимый тип товара по названию и параметрам (README §2–§9)."""

    def classify(self, row_item: RowItem) -> str:
        """Вернуть каноничный тип; пустая строка — не определено."""
        text = normalize_text(row_item.identity.title)
        tech = replace_homoglyphs(text)
        non_tire = _non_tire_product(text, tech)
        if non_tire:
            return non_tire
        if _has_any(text, _SPEC_WORDS):
            return SPECIAL
        if _has_any(text, _MOTO_WORDS):
            return MOTO
        size = _parse_size(tech, row_item)
        if size is None:
            return ''
        if isinstance(size, _SpecialForm) or _is_special(text, tech, size):
            return SPECIAL
        if _declared_commercial(row_item):
            size = _as_commercial(size)
        if _is_moto(size):
            return MOTO
        return _family(size, text, tech)


def _non_tire_product(text: str, tech: str) -> str | None:
    """Тип нешинной позиции по слову названия (кольцо → камера → лента → диск)."""
    if 'уплотнительн' in text and 'кольц' in text:
        return O_RING
    if _is_camera(text):
        return CAMERA
    if 'лент' in text:
        return RIM_TAPE
    if 'диск' in text:
        return DISK
    if 'кольц' in text and re.search(r'r\d|d\s*=|\d+\s*-\s*\d+', tech):
        return O_RING
    if _looks_like_disk(tech):
        return DISK
    return None


def _is_camera(text: str) -> bool:
    """Слово `камер` как товар; `под камеру`/`камерная` — не камера.

    `под камеру` — признак бескамерного диска; `камерная`/`бескамерная` — тип
    шины (с камерой / без камеры). Оба содержат `камер`, но камерой как товаром
    не являются.
    """
    if 'под камер' in text or 'камерн' in text:
        return False
    return 'камер' in text


def _looks_like_disk(tech: str) -> bool:
    """Диск по посадочному месту: `ширина×диаметр` вместе с разболтовкой/слэшем.

    Одной пары `NxM` мало: у штемпелеванных дисков их две (`8.5x20 10x335`),
    либо за шириной идёт `/` (`5,5x16/6x170`). Иначе модель вида `ET500`
    у шины принималась бы за вылет диска.
    """
    if _DISK_PAIR_SLASH.search(tech):
        return True
    return len(_DISK_PAIR.findall(tech)) >= 2


def _parse_size(tech: str, row_item: RowItem) -> _Size | None:
    """Разобрать размер из названия; иначе собрать из структурированных полей."""
    parsed = _parse_title_size(tech)
    if parsed is not None:
        return parsed
    return _size_from_fields(row_item)


def _parse_title_size(tech: str) -> _Size | None:
    """Найти форму размера в нормализованном названии (README §4)."""
    match = _METRIC2.search(tech)
    if match is not None:
        return _Metric(
            width=_dimension(match.group(1)),
            profile=_dimension(match.group(2)),
            diameter=_dimension(match.group(3)),
        )
    match = _METRIC.search(tech)
    if match is not None:
        return _Metric(
            width=_dimension(match.group(1)),
            profile=_dimension(match.group(2)),
            diameter=_dimension(match.group(3)),
            commercial=match.group(4) is not None,
        )
    match = _FLOTATION.search(tech)
    if match is not None:
        return _Flotation(diameter=_dimension(match.group(3)), commercial=match.group(4) is not None)
    match = _WIDTH_ONLY.search(tech)
    if match is not None:
        return _WidthOnly(diameter=_dimension(match.group(2)), commercial=match.group(3) is not None)
    match = _INCH.search(tech)
    if match is not None:
        return _Inch(
            width=_dimension(match.group(1)),
            diameter=_dimension(match.group(2)),
            commercial=match.group(3) is not None,
        )
    if _SLASH_DASH.search(tech) or _AGRO_LR.search(tech):
        return _SpecialForm()
    match = _DASH.search(tech)
    if match is not None:
        return _Dash(width_raw=match.group(1), diameter=_dimension(match.group(2)))
    return None


def _size_from_fields(row_item: RowItem) -> _Metric | None:
    """Собрать размер из разобранных полей, если название не дало формы."""
    width = _number(row_item.tire.width)
    diameter = _number(row_item.tire.diameter)
    if width is None or diameter is None:
        return None
    return _Metric(width=width, diameter=diameter, profile=_number(row_item.tire.height_percent))


def _as_commercial(size: _TireSize) -> _TireSize:
    """Размер с признаком коммерческой шины; у диагонали признака нет."""
    if isinstance(size, _Dash):
        return size
    return replace(size, commercial=True)


def _is_special(text: str, tech: str, size: _TireSize) -> bool:
    """Спецшина: код TRA, агро-индекс или большой посадочный диаметр (без слов-маркеров)."""
    if _TRA.search(tech):
        return True
    if _AGRO_AI.search(tech) and not _has_any(text, _AXLE_WORDS) and not _has_truck_pr(tech):
        return True
    return size.diameter >= _AGRO_MIN_DIAMETER


def _is_moto(size: _TireSize) -> bool:
    """Мотошина по размеру: малый метрический без коммерческих признаков.

    Слова-маркеры (`мото`, `скутер`…) проверяет `classify` раньше разбора размера.
    """
    if not isinstance(size, _Metric) or size.commercial:
        return False
    return (
        size.width <= _MOTO_MAX_WIDTH
        and size.diameter <= _MOTO_MAX_DIAMETER
        and _at_least(size.profile, _MOTO_MIN_PROFILE)
    )


def _family(size: _TireSize, text: str, tech: str) -> str:
    """Семья шины по форме размера, диаметру, PR, индексу нагрузки и оси."""
    if isinstance(size, _Metric):
        return _metric_family(size, text, tech)
    if isinstance(size, _WidthOnly):
        return _width_only_family(size, tech)
    if isinstance(size, _Inch):
        return _inch_family(size, text, tech)
    if isinstance(size, _Flotation):
        return _flotation_family(size)
    return TRUCK if _is_truck_dash(size) else SPECIAL


def _flotation_family(size: _Flotation) -> str:
    """Флотация `NNxNN R NN`: посадочный ≥ 15 — SUV-шина, меньше — индустрия.

    `31x10.5R15`/`35x12.5R17` — легковые грязевые для внедорожников и пикапов;
    `24x10-11` — индустриальные/квадро с малым посадочным (README §4е).
    """
    if size.commercial:
        return LIGHT_TRUCK
    if size.diameter >= _SUV_FLOTATION_RIM:
        return PASSENGER
    return SPECIAL


def _metric_family(size: _Metric, text: str, tech: str) -> str:
    """Легковая / легкогрузовая / грузовая по метрическому размеру (README §5.3–§5.5)."""
    if size.commercial:
        return LIGHT_TRUCK
    if _has_any(text, _AXLE_WORDS):
        return TRUCK
    diameter = size.diameter
    width = size.width
    if diameter == _AGRO_WIDE_DIAMETER and width >= _AGRO_WIDE_WIDTH:
        return SPECIAL
    if diameter in _TRUCK_DIAMETERS or diameter == _AGRO_WIDE_DIAMETER:
        return TRUCK
    if _double_load(tech) and diameter >= _TRUCK_DIAMETER_MIN:
        return TRUCK
    if diameter >= _TRUCK_DIAMETER_MIN and _at_least(size.profile, _TRUCK_PROFILE_HIGH):
        return TRUCK
    if diameter >= _TRUCK_DIAMETER_MIN and width >= _TRUCK_WIDTH_WIDE and _at_least(size.profile, _TRUCK_PROFILE_MIN):
        return TRUCK
    if _double_load(tech) and 13 <= diameter <= 17:
        return LIGHT_TRUCK
    if _is_commercial(tech):
        return LIGHT_TRUCK
    return PASSENGER


def _width_only_family(size: _WidthOnly, tech: str) -> str:
    """Трёхзначная ширина без профиля (`165 R13`): грузовая только по большому диаметру."""
    if size.commercial:
        return LIGHT_TRUCK
    if size.diameter >= 17.5:
        return TRUCK
    if _has_truck_pr(tech):
        return TRUCK
    return PASSENGER


def _inch_family(size: _Inch, text: str, tech: str) -> str:
    """Дюймовый / десятичный размер (README §4б, §5.3)."""
    if size.commercial:
        return LIGHT_TRUCK
    if _has_any(text, _AXLE_WORDS):
        return TRUCK
    diameter = size.diameter
    first = size.width
    if diameter in _TRUCK_DIAMETERS or diameter == 20:
        return TRUCK
    if _has_truck_pr(tech):
        return TRUCK
    if first >= 10:
        return TRUCK
    if diameter == 16 and first >= 7:
        return TRUCK
    if _is_commercial(tech):
        return LIGHT_TRUCK
    return SPECIAL


def _is_truck_dash(size: _Dash) -> bool:
    """Дюймовая диагональ (`11.00-20`) — грузовая; иначе индустрия/сельхоз."""
    if not _TRUCK_DASH_DIAMETER_MIN <= size.diameter <= _TRUCK_DASH_DIAMETER_MAX:
        return False
    return _TRUCK_DASH_WIDTH.fullmatch(size.width_raw) is not None


def _double_load(tech: str) -> bool:
    """Есть двойной индекс нагрузки (`152/149`) с двумя большими числами."""
    for first, second in _DOUBLE_LOAD.findall(tech):
        if int(first) >= _LOAD_INDEX_SCALE and int(second) >= _LOAD_INDEX_SCALE:
            return True
    return False


def _has_truck_pr(tech: str) -> bool:
    """Слойность PR в названии (`14PR`, `PR16`) не ниже грузовой."""
    tokens = _PR_BEFORE.findall(tech) + _PR_AFTER.findall(tech)
    return any(int(token) >= _TRUCK_PR for token in tokens)


def _is_commercial(tech: str) -> bool:
    """Фургонные/коммерческие маркеры модели (README §5.4).

    Латиница ищется по границам слова: иначе ``AdvanteX`` (содержит ``van``)
    и ``RXQuest`` ошибочно помечались бы коммерческими.
    """
    return any(re.search(rf'(?<![a-z]){re.escape(word)}(?![a-z])', tech) for word in _COMMERCIAL_WORDS)


def _declared_commercial(row_item: RowItem) -> bool:
    """Поставщик пометил легкогрузовую: `C`/`LT`/`CP` в поле `tire_type`.

    У mim в колонке «Тип авто» стоят `C` (commercial) и `LT` (light truck) —
    это признак легкогрузовой шины, даже если суффикса нет в названии (README §5.4).
    """
    raw = row_item.tire.tire_type
    if not raw:
        return False
    return raw.strip().lower() in _COMMERCIAL_MARKERS


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def _number(raw: str | None) -> float | None:
    """Число из поля позиции (`'22,5'` → ``22.5``); None — пусто/не число."""
    if not raw:
        return None
    try:
        return float(raw.replace(',', '.'))
    except ValueError:
        return None


def _dimension(raw: str) -> float:
    """Число из группы регулярки размера: цифры и точка (запятую убрал `normalize_text`)."""
    return float(raw)


def _at_least(measure: float | None, bound: float) -> bool:
    """Известное значение не меньше границы; неизвестное — нет."""
    return measure is not None and measure >= bound
