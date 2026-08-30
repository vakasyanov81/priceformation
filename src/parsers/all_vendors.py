"""
collection all active vendors
"""

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.vendors.autosnab54_ru import Autosnab54Parser, autosnab_config
from parsers.vendors.four_tochki.four_tochki_sheet1 import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_config,
)
from parsers.vendors.four_tochki.four_tochki_sheet2 import (
    FourTochkiParser2Sheet,
    fourtochki_sheet_2_config,
)
from parsers.vendors.mim.mim_1sheet import MimParser1Sheet, mim_sheet_1_config
from parsers.vendors.mim.mim_2sheet import MimParser2Sheet, mim_sheet_2_config
from parsers.vendors.mim.mim_3sheet import MimParser3Sheet, mim_sheet_3_config
from parsers.vendors.pioner import PionerParser, pioner_config
from parsers.vendors.poshk import PoshkParser, poshk_config
from parsers.vendors.stk import STKParser, stk_config
from parsers.vendors.zapaska_disk_json import ZapaskaDiskJSON, zapaska_config
from parsers.vendors.zapaska_tire_json import ZapaskaTireJSON, zapaska_tire_config

SupplierName = str
SupplierCode = str

type VendorEntry = tuple[type[BaseParser], ParseConfiguration]


def all_vendors() -> list[VendorEntry]:
    """get all active vendors"""
    return [
        (MimParser1Sheet, mim_sheet_1_config),
        (MimParser2Sheet, mim_sheet_2_config),
        (MimParser3Sheet, mim_sheet_3_config),
        (FourTochkiParser1Sheet, fourtochki_sheet_1_config),
        (FourTochkiParser2Sheet, fourtochki_sheet_2_config),
        (PionerParser, pioner_config),
        (PoshkParser, poshk_config),
        (ZapaskaDiskJSON, zapaska_config),
        (ZapaskaTireJSON, zapaska_tire_config),
        (Autosnab54Parser, autosnab_config),
        (STKParser, stk_config),
    ]


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
            "sup_code": supplier.folder_name,
            "sup_title": supplier.name,
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
