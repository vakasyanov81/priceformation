"""Канонические типы товара и синонимы поставщиков (README_ProductType.md §1, §7).

Единый словарь типов для независимого классификатора (`product_type.py`) и
слоя категорий (`category_finder`): канонические имена, карта синонимов
поставщиков и сверка заявленного типа с вычисленным.

Модуль чистый: без IO и знания о позиции строки. `declared_matches` работает
над строками «заявленный тип» и «свой тип», поэтому не тянет `RowItem`.
"""

from __future__ import annotations

from parsers.strategies.normalize import normalize_text

PASSENGER = 'Легковая шина'
LIGHT_TRUCK = 'Легкогрузовая шина'
TRUCK = 'Грузовая шина'
SPECIAL = 'Спецшина'
MOTO = 'Мотошина'
CAMERA = 'Автокамера'
RIM_TAPE = 'Ободная лента'
O_RING = 'Уплотнительное кольцо'
DISK = 'Диск'

GENERIC_TIRE = 'Автошина'
OTHER = 'Прочие'

CANONICAL_TYPES: tuple[str, ...] = (
    PASSENGER,
    LIGHT_TRUCK,
    TRUCK,
    SPECIAL,
    MOTO,
    CAMERA,
    RIM_TAPE,
    O_RING,
    DISK,
)

# Карта категории поставщика: канонический тип → слова, встречающиеся в прайсах.
# Используется `category_finder.map_categories` (поиск категории по названию).
CATEGORY_ALIASES: dict[str, tuple[str, ...]] = {
    TRUCK: ('грузовая',),
    LIGHT_TRUCK: ('легкогрузовая',),
    PASSENGER: ('легковая', 'грязевая'),
    SPECIAL: ('спецшина', 'сельхоз'),
    MOTO: ('мотошина', 'квадроциклы'),
    CAMERA: ('камеры', 'камера', 'автокамеры'),
    DISK: ('диски', 'автодиск', 'автодиски'),
    RIM_TAPE: ('о/лента', 'лента', 'ленты'),
}

# Общие/неспецифичные ярлыки: сверять нельзя (README §7 п.4).
_GENERIC_LABELS = frozenset(
    (
        '',
        'шина',
        'шины',
        'автошина',
        'автошины',
        'автопокрышка',
        'автопокрышки',
        GENERIC_TIRE.lower(),
        OTHER.lower(),
        'прочее',
    ),
)

# Конкретные ярлыки поставщиков → канонический тип (README §7, таблица).
_DECLARED_ALIASES: dict[str, str] = {
    'легковая': PASSENGER,
    'легковая шина': PASSENGER,
    'suv': PASSENGER,
    'cuv': PASSENGER,
    'грязевая': PASSENGER,
    'легкогрузовая': LIGHT_TRUCK,
    'легкогрузовая шина': LIGHT_TRUCK,
    'c': LIGHT_TRUCK,
    'lt': LIGHT_TRUCK,
    'cp': LIGHT_TRUCK,
    'van': LIGHT_TRUCK,
    'коммерческая': LIGHT_TRUCK,
    'грузовая': TRUCK,
    'грузовая шина': TRUCK,
    'груз': TRUCK,
    'груз.': TRUCK,
    'спецшина': SPECIAL,
    'спецтехника': SPECIAL,
    'сельхоз': SPECIAL,
    'сельхозшина': SPECIAL,
    'индустриальная': SPECIAL,
    'спецпокрышка': SPECIAL,
    'мото': MOTO,
    'мотошина': MOTO,
    'автокамера': CAMERA,
    'камера': CAMERA,
    'камеры': CAMERA,
    'диск': DISK,
    'автодиск': DISK,
    'колесо': DISK,
    'ободная лента': RIM_TAPE,
    'о/лента': RIM_TAPE,
    'об/лента': RIM_TAPE,
    'об/л': RIM_TAPE,
    'флиппер': RIM_TAPE,
    'лента': RIM_TAPE,
    'уплотнительное кольцо': O_RING,
    'кольцо': O_RING,
}


def canonical_declared(declared: str | None) -> str | None:
    """Канонизировать заявленный поставщиком тип; None — общий/пустой/неизвестный."""
    label = normalize_text(declared)
    if not label or label in _GENERIC_LABELS:
        return None
    return _DECLARED_ALIASES.get(label)


def declared_matches(declared: str | None, own: str) -> bool:
    """Совпадает ли заявленный тип с вычисленным (True — расхождения нет).

    Расхождения нет, если свой тип пуст, заявленный общий/пустой/неизвестный,
    или канонизированный заявленный равен вычисленному (README §7 п.4).
    """
    if not own:
        return True
    canonical = canonical_declared(declared)
    if canonical is None:
        return True
    return canonical == own
