"""Модели конфигурации поставщика: parse_config/vendors/<folder>.json."""

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import Any

from domain.exceptions import ConfigValidationError
from domain.row_item.field_registry import spec_of
from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object, read_zero_one_flag
from parsers.vendor_config.fields import read_int, read_int_list, read_str_list, read_str_map, read_text
from parsers.vendor_config.slot_configs import (
    BehaviorConfig,
    CategoryConfig,
    PricingConfig,
    TitleConfig,
)

READER_XLS = 'xls'
READER_JSON = 'json'
_READERS = (READER_XLS, READER_JSON)
_MSG_COLUMNS = 'не заданы «columns»: ни в секции, ни у поставщика'
_MSG_TEMPLATES = 'не задан «file_templates»: ни в секции, ни у поставщика'
_COLUMNS_HINT = 'ожидается ключ из реестра полей RowItem'


@dataclass(frozen=True, slots=True)
class VendorSection:
    """Один лист/файл поставщика: колонки, идентификаторы каталога и слоты."""

    id: str
    name: str
    start_row: int
    file_templates: tuple[str, ...]
    columns: dict[int | str, str]
    sheet_info: str = ''
    sheet_indexes: tuple[int, ...] = ()
    category: CategoryConfig = field(default_factory=CategoryConfig)
    title: TitleConfig = field(default_factory=TitleConfig)
    pricing: PricingConfig = field(default_factory=PricingConfig)

    @classmethod
    def from_dict(cls, raw: Any, where: str, vendor: VendorConfig) -> VendorSection:
        """Разобрать секцию: отсутствующие ключи берутся у поставщика."""
        payload = as_config_object(raw, where)
        file_templates = read_str_list(payload, 'file_templates', where, vendor.file_templates)
        if not file_templates:
            raise ConfigValidationError(f'{where}: {_MSG_TEMPLATES}')
        columns = _read_columns(payload, where, vendor.reader) or vendor.columns
        if not columns:
            raise ConfigValidationError(f'{where}: {_MSG_COLUMNS}')
        return cls(
            id=read_text(payload, 'id', where, vendor.code),
            name=read_text(payload, 'name', where, vendor.name),
            start_row=read_int(payload, 'start_row', where, vendor.start_row),
            file_templates=file_templates,
            columns=columns,
            sheet_info=read_text(payload, 'sheet_info', where, ''),
            sheet_indexes=read_int_list(payload, 'sheet_indexes', where),
            category=_read_slot(payload, 'category', where, vendor.category, CategoryConfig.from_dict),
            title=_read_slot(payload, 'title', where, vendor.title, TitleConfig.from_dict),
            pricing=_read_slot(payload, 'pricing', where, vendor.pricing, PricingConfig.from_dict),
        )


@dataclass(frozen=True, slots=True)
class VendorConfig:
    """Конфиг одного поставщика (одна папка в file_prices)."""

    folder: str
    enabled: bool
    code: str
    name: str
    start_row: int
    file_templates: tuple[str, ...] = ()
    reader: str = READER_XLS
    columns: dict[int | str, str] = field(default_factory=dict)
    pricing: PricingConfig = field(default_factory=PricingConfig)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    category: CategoryConfig = field(default_factory=CategoryConfig)
    title: TitleConfig = field(default_factory=TitleConfig)
    sections: tuple[VendorSection, ...] = ()

    @classmethod
    def from_dict(cls, raw: Any, folder: str, where: str) -> VendorConfig:
        """Разобрать конфиг; `folder` — имя файла без расширения, `where` — путь до ключа в ошибках."""
        payload = as_config_object(raw, where)
        reader = read_text(payload, 'reader', where, READER_XLS)
        if reader not in _READERS:
            raise ConfigValidationError(f'{where}: «reader» должен быть «xls» или «json», получено {reader!r}')
        config = cls(
            folder=folder,
            enabled=read_zero_one_flag(payload, 'enabled', where),
            code=read_text(payload, 'code', where),
            name=read_text(payload, 'name', where),
            start_row=read_int(payload, 'start_row', where),
            file_templates=read_str_list(payload, 'file_templates', where),
            reader=reader,
            columns=_read_columns(payload, where, reader),
            pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
            behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
            category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
            title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
            sections=(),
        )
        return replace(config, sections=_read_sections(payload, where, config))


def _read_sections(payload: RawConfig, where: str, vendor: VendorConfig) -> tuple[VendorSection, ...]:
    """Разобрать секции: отсутствующий или пустой список — ошибка."""
    sections_raw = payload.get('sections')
    if not isinstance(sections_raw, list) or not sections_raw:
        raise ConfigValidationError(f'{where}: «sections» должно быть непустым списком, получено {sections_raw!r}')
    return tuple(
        VendorSection.from_dict(section, f'{where} → sections[{index}]', vendor)
        for index, section in enumerate(sections_raw)
    )


def _read_slot[ResultT](
    payload: RawConfig,
    key: str,
    where: str,
    default: ResultT,
    parse: Callable[[Any, str], ResultT],
) -> ResultT:
    """Прочитать слот, если ключ задан, иначе вернуть значение по умолчанию."""
    if key not in payload:
        return default
    section = f'{where} → {key}'
    return parse(as_config_object(payload[key], section), section)


def _read_columns(payload: RawConfig, where: str, reader: str) -> dict[int | str, str]:
    """Колонки: для xls ключи — индексы колонок, для json — ключи исходной записи."""
    raw_columns = read_str_map(payload, 'columns', where)
    if reader == READER_JSON:
        parsed: dict[int | str, str] = {key: name for key, name in raw_columns.items()}
    else:
        parsed = {}
        for key, name in raw_columns.items():
            parsed[_column_index(key, f'{where} → {key}')] = name
    _ensure_known_fields(parsed, where)
    return parsed


def _ensure_known_fields(columns: dict[int | str, str], where: str) -> None:
    """Проверить, что колонка указывает на известное плоское поле позиции (реестр RowItem)."""
    for source, name in columns.items():
        if spec_of(name) is None:
            raise ConfigValidationError(
                f'{where} → columns[{source}]: неизвестное поле «{name}»; {_COLUMNS_HINT}',
            )


def _column_index(column_key: str, where: str) -> int:
    """Индекс колонки xls из строкового ключа JSON-конфига."""
    if not column_key.isdigit():
        raise ConfigValidationError(f'{where}: ключ колонки для reader «xls» должен быть целым, получен {column_key!r}')
    return int(column_key)
