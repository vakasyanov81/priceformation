"""
collection all active vendors (config-driven)
"""

from __future__ import annotations

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.registry import all_vendors_from_registry
from parsers.vendor_config.provider import load_vendor_configs

SupplierName = str
SupplierCode = str

type VendorEntry = tuple[type[BaseParser], ParseConfiguration]


def all_vendors() -> list[VendorEntry]:
    """get all active vendors (from registry, config-driven)"""
    return all_vendors_from_registry()


def all_vendor_supplier_info() -> dict[SupplierCode, SupplierName]:
    """Все поставщики: код → название, без учёта enabled."""
    supplier_info: dict[SupplierCode, SupplierName] = {}
    for config in load_vendor_configs().values():
        for section in config.sections:
            supplier_info[section.id] = section.name
    return supplier_info


def all_vendor_supplier_catalog() -> dict[SupplierCode, dict[str, str]]:
    """Все поставщики: код → folder (folder_name) и название (sup_title)."""
    catalog: dict[SupplierCode, dict[str, str]] = {}
    for config in load_vendor_configs().values():
        for section in config.sections:
            catalog[section.id] = {
                'sup_code': config.folder,
                'sup_title': section.name,
            }
    return catalog


def split_vendor_supplier_info() -> tuple[dict[SupplierCode, SupplierName], dict[SupplierCode, SupplierName]]:
    """Активные и отключённые поставщики: код → название."""
    enabled: dict[SupplierCode, SupplierName] = {}
    disabled: dict[SupplierCode, SupplierName] = {}
    for config in load_vendor_configs().values():
        for section in config.sections:
            target = enabled if config.enabled else disabled
            target[section.id] = section.name
    return enabled, disabled
