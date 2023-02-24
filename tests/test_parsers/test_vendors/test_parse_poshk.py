# -*- coding: utf-8 -*-
"""
tests for Poshk vendor after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List, Tuple

import pytest

from parsers import data_provider
from parsers.base_parser.base_parser_config import BasePriceParseConfigurationParams
from parsers.row_item.row_item import RowItem
from parsers.vendors.poshk import PoshkParser, PoshkPriceParseConfiguration
from parsers.xls_reader import FakeXlsReader
from tests.test_base_parser.test_manufacturer_finder import map_manufacturer
from tests.test_parsers.fixtures.poshk import poshk_one_item_result

vendor_list_config = {
    "poshk": {"enabled": 1},
    "zapaska": {"enabled": 1},
    "mim": {"enabled": 1},
    "pioner": {"enabled": 1},
    "four_tochki": {"enabled": 1},
}


class MarkupRulesProviderForTests(data_provider.MarkupRulesProviderBase):
    """markup rules data provider for tests"""

    def get_markup_data(self):
        """get markup rules"""
        return {
            "markup_rules": {
                "rule_70": {"min": 0, "max": 200, "percent": 0.7},
                "rule_50": {"min": 200, "max": 300, "percent": 0.5},
                "rule_40": {"min": 300, "max": 500, "percent": 0.4},
                "rule_30": {"min": 500, "max": 1500, "percent": 0.3},
                "rule_25": {"min": 1500, "max": 5000, "percent": 0.25},
                "rule_15": {"min": 5000, "max": 8000, "percent": 0.15},
                "rule_14": {"min": 8000, "max": 20000, "percent": 0.14},
                "rule_8": {"min": 20000, "max": 30000, "percent": 0.08},
                "rule_7": {"min": 30000, "max": 60000, "percent": 0.07},
            }
        }


class ManufacturerAliasesProviderForTests(
    data_provider.ManufacturerAliasesProviderBase
):
    """manufacturer aliases data provider for tests"""

    def get_aliases(self) -> dict:
        """get manufacturer aliases"""
        return map_manufacturer


class BlackListProviderForTests(data_provider.BlackListProviderBase):
    """black list data provider for tests"""

    def get_black_list_data(self) -> list:
        """get black list"""
        return ["wrong title", "wrong title 2"]


class StopWordsProviderForTests(data_provider.StopWordsProviderBase):
    """stop words data provider for tests"""

    def get_stop_words_data(self) -> list:
        """get stop word list"""
        return ["некондиция", "2 сорт", "восстановленная"]


class VendorListProviderForTests(data_provider.VendorListProviderBase):
    """Base data provider with supplier config"""

    def __init__(self, config):
        """set test config"""
        self.config = config or {}

    def get_config_vendor_list(self):
        """get config"""
        return self.config


parser_config = BasePriceParseConfigurationParams(
    black_list_provider=BlackListProviderForTests(),
    markup_rules_provider=MarkupRulesProviderForTests(),
    stop_words_provider=StopWordsProviderForTests(),
    vendor_list=VendorListProviderForTests(vendor_list_config),
    manufacturer_aliases=ManufacturerAliasesProviderForTests(),
)


def get_fake_parser(parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return PoshkParser(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        price_config=PoshkPriceParseConfiguration(parser_config),
    )


def test_parse():
    """check all field for one price-row"""

    result: List[RowItem] = get_fake_parser(poshk_one_item_result()).get_result()

    assert len(result) == 1
    assert result[0].title == "10-16.5 Nortec ER-218 10PR 135B TL спецшина"
    assert result[0].type_production == "Автошина"
    assert result[0].price_markup == 6070
    assert result[0].supplier_name == "Пошк"
    assert result[0].percent_markup == 25.0


@pytest.mark.parametrize(
    "title, prepared_title",
    [
        # remove whitespace
        ("385/65 R22.5 ...", "385/65R22.5 ..."),
        ("385/65  R22.5 ...", "385/65R22.5 ..."),
        ("10.00 R20 ...", "10.00R20 ..."),
        # replace * -> x
        ("... 31*10.5-15 ...", "... 31x10.5-15 ..."),
        ("... bla 6.75*19.5 6*222.25 ...", "... bla 6.75x19.5 6x222.25 ..."),
        ("... i*cept", "... i*cept"),
    ],
)
def test_prepare_title(title, prepared_title):
    """check prepare title"""

    item = RowItem({"title": title})
    title = PoshkParser.prepare_title(item.title)

    assert title == prepared_title


class TestParsePoshk:
    """
    tests for Poshk vendor after raw-parser process
    """

    @pytest.mark.parametrize(
        "title, category",
        [
            ("some product", "Разное"),
            ("some диск product", "Диск"),
            ("some ободная лента product", "Ободная лента"),
            ("some шина product", "Автошина"),
            ("some покрышка product", "Автошина"),
            ("some камера product", "Автокамера"),
        ],
    )
    def test_set_category(self, title, category):
        """test define category name by title"""
        parse_result, first_row = self.get_first_row_item(poshk_one_item_result())
        first_row.title = title
        result: List[RowItem] = get_fake_parser(parse_result).get_result()
        assert result[0].type_production == category

    @classmethod
    def get_first_row_item(cls, _result) -> Tuple[dict, RowItem]:
        """get first item from parse result"""
        file = list(_result.keys())[0]
        return _result, RowItem(_result[file][0])

    @pytest.mark.parametrize(
        "price, price_with_markup",
        [
            (100, 170),
            (150, 260),
            (200, 340),
            (210, 320),
            (250, 380),
            (300, 450),
            (350, 490),
            (500, 700),
            (1000, 1300),
            (1500, 1950),
            (2000, 2500),
            (3000, 3750),
            (3500, 4380),
            (5000, 6250),
            (9000, 10270),
            (10000, 11410),
            (15000, 17110),
            (20000, 22810),
            (25000, 27000),
            (30000, 32410),
            (35000, 37450),
            (40000, 42800),
            (45000, 48150),
            (50000, 53500),
            (55000, 58850),
            (60000, 64210),
            (70000, 74900),
            (100000, 107000),
        ],
    )
    def test_markup(self, price, price_with_markup):
        """test calculation price-markup"""
        parse_result, first_row = self.get_first_row_item(poshk_one_item_result())
        first_row.price_opt = price

        parser = get_fake_parser(parse_result)

        result: List[RowItem] = parser.get_result()

        assert result[0].price_markup == price_with_markup

    @pytest.mark.parametrize(
        "title",
        [
            "some некондиция product",
            "some 2 сорт product",
            "185/75 R16 Forward Dinamic 156 92Q TL автопокрышка (ВОССТАНОВЛЕННАЯ), , шт",
        ],
    )
    def test_stop_words(self, title):
        """test exclude price position by stop word in title"""
        parse_result, first_row = self.get_first_row_item(poshk_one_item_result())
        first_row.title = title

        result: List[RowItem] = get_fake_parser(parse_result).get_result()

        assert len(result) == 0
