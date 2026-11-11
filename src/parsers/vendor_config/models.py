"""Модели конфигурации поставщика: parse_config/vendors/<folder>.json."""

from dataclasses import dataclass, field, replace
from typing import Any

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object
from parsers.vendor_config.columns import COLUMNS_KEY, read_columns
from parsers.vendor_config.common import CommonVendorSettings, legacy_defaults
from parsers.vendor_config.fields import read_int, read_str_list, read_text
from parsers.vendor_config.group_loading import read_group
from parsers.vendor_config.group_models import GroupConfig, TireAndDiskConfig
from parsers.vendor_config.group_schema import read_group_payloads
from parsers.vendor_config.merge import merge_config
from parsers.vendor_config.section_models import VendorSection
from parsers.vendor_config.slot_configs import (
    BehaviorConfig,
    CategoryConfig,
    PricingConfig,
    TitleConfig,
)
from parsers.vendor_config.source import SOURCE_FILE

READER_XLS = 'xls'
READER_JSON = 'json'
_READERS = (READER_XLS, READER_JSON)
DEFAULT_START_ROW = 1
# Настройки поставщика, которые секция наследует (и дополняет своими).
_INHERITED_KEYS = ('start_row', 'file_templates', COLUMNS_KEY, 'category', 'title', 'pricing', 'behavior')


@dataclass(frozen=True, slots=True)
class VendorConfig:
    """Конфиг одного поставщика (одна папка в file_prices)."""

    folder: str
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
    source: str = SOURCE_FILE
    enabled: bool = True
    configured_groups: tuple[GroupConfig, ...] = ()

    @property
    def product_groups(self) -> tuple[GroupConfig, ...]:
        """Представить старую схему единственной группой без повторного разбора настроек."""
        return self.configured_groups or (TireAndDiskConfig(self.sections, self.behavior),)

    @classmethod
    def from_dict(
        cls, raw: Any, folder: str, where: str, *, common: CommonVendorSettings | None = None
    ) -> VendorConfig:
        """Разобрать конфиг; `folder` — имя файла без расширения, `where` — путь до ключа в ошибках."""
        payload = as_config_object(raw, where)
        common = common or CommonVendorSettings()
        if 'product_groups' in payload:
            return _read_grouped_vendor(payload, folder, where, common)
        if 'row_selector' in payload:
            raise ConfigValidationError(f'{where} → row_selector: селектор задаётся только в секции')
        payload = merge_config(legacy_defaults(common), payload)
        reader = read_text(payload, 'reader', where, READER_XLS)
        if reader not in _READERS:
            raise ConfigValidationError(f'{where}: «reader» должен быть «xls» или «json», получено {reader!r}')
        config = cls(
            folder=folder,
            code=read_text(payload, 'code', where),
            name=read_text(payload, 'name', where),
            start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
            file_templates=read_str_list(payload, 'file_templates', where, ()),
            reader=reader,
            columns=read_columns(payload, where, reads_json=reader == READER_JSON),
            pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
            behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
            category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
            title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
            sections=(),
            source=read_text(payload, 'source', where, SOURCE_FILE),
        )
        return replace(config, sections=_read_sections(payload, where, config))


def _read_sections(payload: RawConfig, where: str, vendor: VendorConfig) -> tuple[VendorSection, ...]:
    """Разобрать секции: отсутствующий или пустой список — ошибка."""
    sections_raw = payload.get('sections')
    if not isinstance(sections_raw, list) or not sections_raw:
        raise ConfigValidationError(f'{where}: «sections» должно быть непустым списком, получено {sections_raw!r}')
    inherited = {key: payload[key] for key in _INHERITED_KEYS if key in payload}
    return tuple(
        VendorSection.from_dict(section, f'{where} → sections[{index}]', vendor, inherited)
        for index, section in enumerate(sections_raw)
    )


def _read_grouped_vendor(payload: RawConfig, folder: str, where: str, common: CommonVendorSettings) -> VendorConfig:
    """Собрать независимые группы; старые атрибуты временно представляют только шинную группу."""
    reader = read_text(payload, 'reader', where, READER_XLS)
    if reader not in _READERS:
        raise ConfigValidationError(f'{where} → reader: допустимы xls или json')
    declarations = read_group_payloads(payload, where, common, reads_json=reader == READER_JSON)
    vendor = VendorConfig(
        folder=folder,
        code=read_text(payload, 'code', where),
        name=read_text(payload, 'name', where),
        start_row=DEFAULT_START_ROW,
        reader=reader,
        source=read_text(payload, 'source', where, SOURCE_FILE),
    )
    groups = tuple(read_group(declaration, vendor) for declaration in declarations)
    tires = next((group for group in groups if isinstance(group, TireAndDiskConfig)), None)
    return replace(
        vendor,
        configured_groups=groups,
        sections=() if tires is None else tires.sections,
        behavior=BehaviorConfig() if tires is None else tires.behavior,
    )
