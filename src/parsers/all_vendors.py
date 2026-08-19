"""
collection all active vendors
"""

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
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
from parsers.vendors.zapaska_tire_json import ZapaskaTireJSON, load_remote_data, zapaska_tire_config

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
    """Supplier info"""
    supplier_info: dict[SupplierCode, SupplierName] = {}
    for _, config in all_vendors():
        supplier_info[config.parse_config.parser_params.supplier.code] = config.parse_config.parser_params.supplier.name
    return supplier_info


def load_remote_vendor_data() -> None:
    """Скачать прайсы с API тех поставщиков, у кого оно есть."""
    load_remote_data()
