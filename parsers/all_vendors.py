# -*- coding: utf-8 -*-
"""
collection all active vendors
"""
__author__ = "Kasyanov V.A."

from typing import List, Tuple, Type

from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.vendors.autosnab54_ru import Autosnab54Parser, autosnab_config
from parsers.vendors.four_tochki.four_tochki_1sheet import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_config,
)
from parsers.vendors.four_tochki.four_tochki_2sheet import (
    FourTochkiParser2Sheet,
    fourtochki_sheet_2_config,
)
from parsers.vendors.mim.mim_1sheet import MimParser1Sheet, mim_sheet_1_config
from parsers.vendors.mim.mim_2sheet import MimParser2Sheet, mim_sheet_2_config
from parsers.vendors.mim.mim_3sheet import MimParser3Sheet, mim_sheet_3_config
from parsers.vendors.pioner import BaseParser, PionerParser, pioner_config
from parsers.vendors.poshk import PoshkParser, poshk_config
from parsers.vendors.stk import STKParser, stk_config
from parsers.vendors.zapaska import ZapaskaPriceAndRestParser, zapaska_config


def all_vendors() -> List[Tuple[Type[BaseParser], Type[ParseConfiguration]] | None]:
    """get all active vendors"""
    return [
        (MimParser1Sheet, mim_sheet_1_config),
        (MimParser2Sheet, mim_sheet_2_config),
        (MimParser3Sheet, mim_sheet_3_config),
        (FourTochkiParser1Sheet, fourtochki_sheet_1_config),
        (FourTochkiParser2Sheet, fourtochki_sheet_2_config),
        (PionerParser, pioner_config),
        (PoshkParser, poshk_config),
        (ZapaskaPriceAndRestParser, zapaska_config),
        (Autosnab54Parser, autosnab_config),
        (STKParser, stk_config),
    ]
