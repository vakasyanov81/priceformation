# -*- coding: utf-8 -*-
"""
tests for four_tochki vendor (sheet 2) after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List
from unittest.mock import patch

from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.four_tochki.four_tochki_2sheet import (
    FourTochkiParser2Sheet,
    fourtochki_sheet_2_params,
)
from test_parsers.fixtures.four_tochki_sheet2 import (
    four_tochki_one_item_result,
    four_tochki_invalid_item_result,
    four_tochki_one_item_result_1,
)
from test_parsers.test_vendors.parse_config import (
    MimMarkupRulesProviderForTests,
    make_parse_configuration,
)

parser_config = make_parse_configuration(fourtochki_sheet_2_params, MimMarkupRulesProviderForTests())


def get_fake_parser(parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return FourTochkiParser2Sheet(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


def test_parse():
    """check all field for one price-row"""

    result: List[RowItem] = get_fake_parser(four_tochki_one_item_result()).parse()

    assert len(result) == 1
    assert result[0].title == "6.5x16 5x114.3 ET45 60.1 MBMF Alcasta M35"
    assert result[0].type_production == "Диск"
    assert result[0].price_markup == 8270
    assert result[0].supplier_name == "Форточки"
    assert result[0].percent_markup == 14.7

    result: List[RowItem] = get_fake_parser(four_tochki_one_item_result_1()).parse()

    assert len(result) == 1
    assert result[0].title == "5.5x14 4x98 ET38 58.6 Алмаз Скад Ягуар (КЛ147)"
    assert result[0].type_production == "Диск"
    assert result[0].price_markup == 8270
    assert result[0].supplier_name == "Форточки"
    assert result[0].percent_markup == 14.7


def test_parse_with_invalid_item():
    """one invalid item is skipped"""

    with patch("core.log_message.log_msg") as mock_log_msg:
        result: List[RowItem] = get_fake_parser(four_tochki_invalid_item_result()).parse()
    assert len(result) == 1
    assert mock_log_msg.call_count == 2

    assert (
        mock_log_msg.mock_calls[0].args[0] == "Не удалось разобрать строку (№ 3) у поставщика: FourTochkiParser2Sheet:"
        " Форточки (Вкладка (диски) #2) // could not convert string to float: 'invalid value'"
    )
    assert mock_log_msg.mock_calls[0].kwargs == {"level": 40, "need_print_log": True}

    assert "Alcasta" in mock_log_msg.mock_calls[1].args[0]
    assert "WHS198858" in mock_log_msg.mock_calls[1].args[0]
    assert mock_log_msg.mock_calls[1].kwargs == {"level": 40, "need_print_log": False}
