"""Колонки секции поставщика: источник (индекс листа xls или ключ JSON-записи) → поле позиции."""

from domain.battery.field_registry import FIELD_KEYS as BATTERY_FIELDS
from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from domain.row_item.field_registry import FIELD_KEYS as TIRE_FIELDS
from parsers.data_provider.json_fields import RawConfig
from parsers.vendor_config.fields import read_str_list, read_str_map

COLUMNS_KEY = 'columns'
_COLUMNS_HINT = 'ожидается ключ из реестра полей выбранной модели'

type Columns = dict[int | str, str]


def read_columns(
    payload: RawConfig, where: str, *, reads_json: bool, group: ProductGroup = ProductGroup.TIRE_AND_DISK
) -> Columns:
    """Колонки: для xls ключи — индексы колонок, для json (`reads_json`) — ключи исходной записи.

    Для json колонки можно задать списком: ключ записи совпадает с полем позиции (`["code", "title"]`).
    """
    if reads_json and isinstance(payload.get(COLUMNS_KEY), list):
        parsed = _same_named_columns(payload, where)
    elif reads_json:
        parsed = _keyed_columns(payload, where)
    else:
        parsed = _indexed_columns(payload, where)
    _ensure_known_fields(parsed, where, group)
    return parsed


def _indexed_columns(payload: RawConfig, where: str) -> Columns:
    """Колонки xls: строковый ключ JSON → индекс колонки."""
    indexed: Columns = {}
    for key, name in read_str_map(payload, COLUMNS_KEY, where).items():
        index = _column_index(key, f'{where} → {key}')
        indexed[index] = name
    return indexed


def _keyed_columns(payload: RawConfig, where: str) -> Columns:
    """Колонки json объектом: ключ исходной записи → поле позиции."""
    keyed: Columns = {}
    keyed.update(read_str_map(payload, COLUMNS_KEY, where))
    return keyed


def _same_named_columns(payload: RawConfig, where: str) -> Columns:
    """Колонки json списком: ключ исходной записи равен имени поля позиции."""
    return {name: name for name in read_str_list(payload, COLUMNS_KEY, where)}


def _ensure_known_fields(columns: Columns, where: str, group: ProductGroup) -> None:
    """Проверить, что колонка указывает на поле реестра выбранной модели."""
    allowed = BATTERY_FIELDS if group is ProductGroup.BATTERIES else TIRE_FIELDS
    for source, name in columns.items():
        if name not in allowed:
            raise ConfigValidationError(
                f'{where} → columns[{source}]: неизвестное поле «{name}» для {group.value}; {_COLUMNS_HINT}',
            )


def _column_index(column_key: str, where: str) -> int:
    """Индекс колонки xls из строкового ключа JSON-конфига."""
    if not column_key.isdigit():
        raise ConfigValidationError(f'{where}: ключ колонки для reader «xls» должен быть целым, получен {column_key!r}')
    return int(column_key)
