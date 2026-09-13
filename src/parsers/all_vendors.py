"""
collection all active vendors
"""

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.registry import all_vendors_from_registry

SupplierName = str
SupplierCode = str

type VendorEntry = tuple[type[BaseParser], ParseConfiguration]


def all_vendors() -> list[VendorEntry]:
    """get all active vendors (from registry)"""
    return all_vendors_from_registry()


def all_vendor_supplier_info() -> dict[SupplierCode, SupplierName]:
    """Все поставщики: код → название, без учёта enabled."""
    supplier_info: dict[SupplierCode, SupplierName] = {}
    for _, config in all_vendors():
        supplier_info[config.supplier.code] = config.supplier.name
    return supplier_info


def all_vendor_supplier_catalog() -> dict[SupplierCode, dict[str, str]]:
    """Все поставщики: код → folder (`sup_code`) и название (`sup_title`)."""
    catalog: dict[SupplierCode, dict[str, str]] = {}
    for _, config in all_vendors():
        supplier = config.supplier
        catalog[supplier.code] = {
            'sup_code': supplier.folder_name,
            'sup_title': supplier.name,
        }
    return catalog


def split_vendor_supplier_info() -> tuple[dict[SupplierCode, SupplierName], dict[SupplierCode, SupplierName]]:
    """Активные и отключённые поставщики: код → название."""
    enabled: dict[SupplierCode, SupplierName] = {}
    disabled: dict[SupplierCode, SupplierName] = {}
    for _, config in all_vendors():
        target = enabled if vendor_config_is_enabled(config) else disabled
        target[config.supplier.code] = config.supplier.name
    return enabled, disabled


def vendor_config_is_enabled(config: ParseConfiguration) -> bool:
    """Поставщик включён в vendor_list.json."""
    try:
        vendor = config.all_vendor_config().get(config.supplier.folder_name)
    except VendorListConfigFileError:
        return False
    return bool(vendor and vendor.enabled)
