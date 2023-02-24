# -*- coding: utf-8 -*-
"""
collection all active vendors
"""
__author__ = "Kasyanov V.A."

from typing import List, Optional, Tuple, Type

from parsers.base_parser.base_parser import BasePriceParseConfiguration
from parsers.vendors.autosnab54_ru import Autosnab54Parser
from parsers.vendors.four_tochki.four_tochki_1sheet import FourTochkiParser1Sheet
from parsers.vendors.four_tochki.four_tochki_2sheet import FourTochkiParser2Sheet
from parsers.vendors.mim.mim_1sheet import MimParser1Sheet
from parsers.vendors.mim.mim_2sheet import MimParser2Sheet
from parsers.vendors.mim.mim_3sheet import MimParser3Sheet
from parsers.vendors.pioner import BaseParser, PionerParser
from parsers.vendors.poshk import PoshkParser
from parsers.vendors.stk import STKParser
from parsers.vendors.zapaska import ZapaskaPriceAndRestParser


def all_vendors() -> (
    List[Tuple[Type[BaseParser], Optional[Type[BasePriceParseConfiguration]]]]
):
    """get all active vendors"""
    return [
        (MimParser1Sheet, BasePriceParseConfiguration),
        (MimParser2Sheet, BasePriceParseConfiguration),
        (MimParser3Sheet, BasePriceParseConfiguration),
        (FourTochkiParser1Sheet, BasePriceParseConfiguration),
        (FourTochkiParser2Sheet, BasePriceParseConfiguration),
        (PionerParser, BasePriceParseConfiguration),
        (PoshkParser, BasePriceParseConfiguration),
        (ZapaskaPriceAndRestParser, BasePriceParseConfiguration),
        (Autosnab54Parser, BasePriceParseConfiguration),
        (STKParser, BasePriceParseConfiguration),
    ]
