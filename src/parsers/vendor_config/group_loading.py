"""Чтение секций в модели выбранной товарной группы."""

from typing import TYPE_CHECKING

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig, read_object
from parsers.vendor_config.battery_settings import BatterySettings
from parsers.vendor_config.columns import read_columns
from parsers.vendor_config.fields import read_int, read_int_list, read_str_list, read_text
from parsers.vendor_config.group_fields import object_list
from parsers.vendor_config.group_models import BatteryConfig, BatterySection, GroupConfig, TireAndDiskConfig
from parsers.vendor_config.group_schema import GroupPayload
from parsers.vendor_config.group_validation import validate_group_settings
from parsers.vendor_config.merge import merge_config
from parsers.vendor_config.row_selector import RowSelector
from parsers.vendor_config.section_models import DEFAULT_START_ROW, VendorSection
from parsers.vendor_config.slot_configs import BehaviorConfig

if TYPE_CHECKING:
    from parsers.vendor_config.models import VendorConfig


def read_group(declaration: GroupPayload, vendor: VendorConfig) -> GroupConfig:
    """Секции получают принадлежность по вложенности, а не по имени листа."""
    parsed_tires: list[VendorSection] = []
    parsed_batteries: list[BatterySection] = []
    for index, section in enumerate(object_list(declaration.settings['sections'], declaration.where)):
        where = f'{declaration.where} → sections[{index}]'
        read_text(section, 'id', f'{where}.id')
        if 'product_group' in section:
            raise ConfigValidationError(f'{where} → product_group: группа определяется вложенностью')
        validate_group_settings(section, where, declaration.id, reads_json=vendor.reader == 'json', section_level=True)
        if declaration.id is ProductGroup.TIRE_AND_DISK:
            parsed_tires.append(VendorSection.from_dict(section, where, vendor, declaration.settings))
        else:
            parsed_batteries.append(_read_battery_section(section, where, declaration.settings, vendor))
    if declaration.id is ProductGroup.BATTERIES:
        return BatteryConfig(tuple(parsed_batteries))
    return TireAndDiskConfig(
        tuple(parsed_tires),
        BehaviorConfig.from_dict(read_object(declaration.settings, 'behavior', declaration.where), declaration.where),
    )


def _read_battery_section(section: RawConfig, where: str, inherited: RawConfig, vendor: VendorConfig) -> BatterySection:
    """Прочитать маршрут и разрешённые наследованием аккумуляторные настройки."""
    payload = merge_config(inherited, section)
    templates = read_str_list(payload, 'file_templates', where, ())
    if not templates:
        raise ConfigValidationError(f'{where} → file_templates: требуется непустой список')
    sheet_indexes = read_int_list(section, 'sheet_indexes', where)
    if vendor.reader == 'json' and sheet_indexes:
        raise ConfigValidationError(f'{where} → sheet_indexes: JSON не содержит листов')
    return BatterySection(
        id=read_text(section, 'id', where),
        name=read_text(section, 'name', where, vendor.name),
        start_row=read_int(payload, 'start_row', where, DEFAULT_START_ROW),
        file_templates=templates,
        sheet_info=read_text(section, 'sheet_info', where, ''),
        sheet_indexes=sheet_indexes,
        row_selector=RowSelector.from_section(section, where),
        config_path=where,
        columns=read_columns(payload, where, reads_json=vendor.reader == 'json', group=ProductGroup.BATTERIES),
        processing=BatterySettings.from_dict(payload, where),
    )
