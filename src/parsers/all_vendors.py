"""
collection all active vendors (config-driven)
"""

from __future__ import annotations

from domain.protocols import ConfigProvider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.registry import all_vendors_including_disabled
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.provider import load_vendor_configs

SupplierName = str
SupplierCode = str

type SupplierDescriptions = dict[SupplierCode, SupplierName | list[SupplierName]]

type VendorEntry = tuple[type[BaseParser], ParseConfiguration]


def all_vendors(config_provider: ConfigProvider) -> list[VendorEntry]:
    """Все поставщики из конфигов, включая отключённых.

    Отключённые тоже попадают в разбор: ``BaseParser.parse`` вернёт пусто и
    залогирует предупреждение «поставщик не активен».
    """
    return all_vendors_including_disabled(config_provider)


def all_vendor_supplier_info(config_provider: ConfigProvider) -> dict[SupplierCode, SupplierName]:
    """Все поставщики: код → название, без учёта enabled."""
    supplier_info: dict[SupplierCode, SupplierName] = {}
    for config in load_vendor_configs(config_provider).values():
        for section in config.all_sections:
            supplier_info[section.id] = section.catalog_name or section.name
    return supplier_info


def all_vendor_supplier_catalog(config_provider: ConfigProvider) -> dict[SupplierCode, dict[str, str]]:
    """Все поставщики: код → folder (folder_name) и название (sup_title)."""
    catalog: dict[SupplierCode, dict[str, str]] = {}
    for config in load_vendor_configs(config_provider).values():
        for section in config.all_sections:
            catalog[section.id] = {
                'sup_code': config.folder,
                'sup_title': section.catalog_name or section.name,
            }
    return catalog


def split_vendor_supplier_info(
    config_provider: ConfigProvider,
) -> tuple[SupplierDescriptions, SupplierDescriptions]:
    """Активные и отключённые поставщики по коду, с названиями их секций."""
    enabled: SupplierDescriptions = {}
    disabled: SupplierDescriptions = {}
    for config in sorted(load_vendor_configs(config_provider).values(), key=_supplier_order):
        names = [section.catalog_name or section.name for section in config.all_sections]
        if not names:
            continue
        target = enabled if config.enabled else disabled
        target[config.code] = _supplier_description(names)
    return enabled, disabled


def _supplier_description(names: list[SupplierName]) -> SupplierName | list[SupplierName]:
    return names[0] if len(names) == 1 else names


def _supplier_order(config: VendorConfig) -> tuple[bool, int, str]:
    """Числовые коды по возрастанию, текстовые — следом по алфавиту."""
    code = config.code
    if code.isdecimal():
        return False, int(code), code
    return True, 0, code
