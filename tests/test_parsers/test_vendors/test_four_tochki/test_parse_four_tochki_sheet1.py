# -*- coding: utf-8 -*-
"""
tests for four_tochki vendor (sheet 1) after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List

from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.row_item.row_item import RowItem
from parsers.vendors.four_tochki.four_tochki_1sheet import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_params,
)
from parsers.xls_reader import FakeXlsReader
from tests.test_parsers.fixtures.four_tochki_sheet1 import four_tochki_many_item_result, four_tochki_one_item_result
from tests.test_parsers.test_vendors.parse_config import (
    MimMarkupRulesProviderForTests,
    make_parse_configuration,
)

parser_config = make_parse_configuration(fourtochki_sheet_1_params, MimMarkupRulesProviderForTests())


def get_fake_parser(parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return FourTochkiParser1Sheet(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


def test_parse():
    """check all field for one price-row"""

    result: List[RowItem] = get_fake_parser(four_tochki_many_item_result()).parse()

    assert len(result) == 3
    assert result[0].title == "205/55R16 BF Goodrich Advantage 94W"
    assert result[0].type_production == "Легковая шина"
    assert result[0].price_markup == 7340
    assert result[0].supplier_name == "Форточки"
    assert result[0].percent_markup == 27.17

    # метрический размер
    assert result[1].title == "31x10.5R15 BF Goodrich All Terrain T/A KO2 109S LT"
    assert result[1].price_markup == 24870
    assert result[1].percent_markup == 27.04

    # грузовая шина
    assert result[2].title == "235/75R17.5 BF Goodrich Route Control D 132/130M"


def test_replace_diameter():
    """check replace RZ -> ZR"""

    result: List[RowItem] = get_fake_parser(four_tochki_one_item_result(diameter="RZ16")).parse()

    assert len(result) == 1
    assert result[0].title == "205/55ZR16 BF Goodrich Advantage 94W"
    assert result[0].type_production == "Легковая шина"
    assert result[0].price_markup == 7340
    assert result[0].supplier_name == "Форточки"
    assert result[0].percent_markup == 27.17
