"""Разрешённые настройки секции шин и дисков."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object
from parsers.vendor_config.columns import read_columns
from parsers.vendor_config.fields import read_int, read_int_list, read_str_list, read_text
from parsers.vendor_config.merge import merge_config
from parsers.vendor_config.row_selector import RowSelector
from parsers.vendor_config.slot_configs import BehaviorConfig, CategoryConfig, PricingConfig, TitleConfig

if TYPE_CHECKING:
    from parsers.vendor_config.models import VendorConfig

READER_JSON = 'json'
DEFAULT_START_ROW = 1
_MSG_COLUMNS = 'не заданы «columns»: ни в секции, ни у поставщика'
_MSG_TEMPLATES = 'не задан «file_templates»: ни в секции, ни у поставщика'


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
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
    row_selector: RowSelector | None = None
    config_path: str = field(default='', compare=False, repr=False)

    @property
    def product_group(self) -> Literal[ProductGroup.TIRE_AND_DISK]:
        """Существующие слоты и колонки секции относятся только к шинам и дискам."""
        return ProductGroup.TIRE_AND_DISK

    @classmethod
    def from_dict(cls, raw: Any, where: str, vendor: VendorConfig, inherited: RawConfig) -> VendorSection:
        """Разобрать секцию поверх настроек поставщика `inherited`: объекты сливаются, значения заменяются."""
        section = as_config_object(raw, where)
        payload = merge_config(inherited, section)
        file_templates = read_str_list(payload, 'file_templates', where, ())
        if not file_templates:
            raise ConfigValidationError(f'{where}: {_MSG_TEMPLATES}')
        columns = read_columns(payload, where, reads_json=vendor.reader == READER_JSON)
        if not columns:
            raise ConfigValidationError(f'{where}: {_MSG_COLUMNS}')
        sheet_indexes = read_int_list(payload, 'sheet_indexes', where)
        if vendor.reader == READER_JSON and sheet_indexes:
            raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
        return cls(
            id=read_text(section, 'id', f'{where}.id'),
            name=read_text(payload, 'name', where, vendor.name),
            start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
            file_templates=file_templates,
            columns=columns,
            sheet_info=read_text(payload, 'sheet_info', where, ''),
            sheet_indexes=sheet_indexes,
            category=CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category'),
            title=TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title'),
            pricing=PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing'),
            behavior=BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior'),
            row_selector=RowSelector.from_section(section, where),
            config_path=where,
        )
