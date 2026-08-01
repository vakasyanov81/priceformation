"""
tests for Poshk vendor after raw-parser process
"""

from typing import Any, List, cast

import pytest
from test_base_parser.test_manufacturer_finder import map_manufacturer
from test_parsers.fixtures.poshk import poshk_one_item_result
from test_parsers.test_vendors.parse_result_helpers import get_first_row_item

from parsers import data_provider
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.poshk import (
    PoshkParser,
    poshk_params,
)

vendor_list_config = {
    "poshk": {"enabled": 1},
    "zapaska": {"enabled": 1},
    "mim": {"enabled": 1},
    "pioner": {"enabled": 1},
    "four_tochki": {"enabled": 1},
}


class MarkupRulesProviderForTests(data_provider.MarkupRulesProviderBase):
    """markup rules data provider for tests"""

    def get_markup_data(self) -> dict[str, Any]:
        """get markup rules"""
        return {
            "markup_rules": {
                "rule_70": {"min": 0, "max": 200, "percent_markup": 0.7},
                "rule_50": {"min": 200, "max": 300, "percent_markup": 0.5},
                "rule_40": {"min": 300, "max": 500, "percent_markup": 0.4},
                "rule_30": {"min": 500, "max": 1500, "percent_markup": 0.3},
                "rule_25": {"min": 1500, "max": 5000, "percent_markup": 0.25},
                "rule_15": {"min": 5000, "max": 8000, "percent_markup": 0.15},
                "rule_14": {"min": 8000, "max": 20000, "percent_markup": 0.14},
                "rule_8": {"min": 20000, "max": 30000, "percent_markup": 0.08},
                "rule_7": {"min": 30000, "max": 60000, "percent_markup": 0.07},
            }
        }


class ManufacturerAliasesProviderForTests(data_provider.ManufacturerAliasesProviderBase):
    """manufacturer aliases data provider for tests"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer aliases"""
        return cast(dict[str, Any], map_manufacturer)


class BlackListProviderForTests(data_provider.BlackListProviderBase):
    """black list data provider for tests"""

    def get_black_list_data(self) -> list[str]:
        """get black list"""
        return ["wrong title", "wrong title 2"]


class StopWordsProviderForTests(data_provider.StopWordsProviderBase):
    """stop words data provider for tests"""

    def get_stop_words_data(self) -> list[str]:
        """get stop word list"""
        return ["некондиция", "2 сорт", "восстановленная"]


class VendorListProviderForTests(data_provider.VendorListProviderBase):
    """Base data provider with supplier config"""

    def __init__(self, config: Any) -> None:
        """set test config"""
        self.config = config or {}

    def get_config_vendor_list(self) -> dict[str, Any]:
        """get config"""
        return cast(dict[str, Any], self.config)


parser_config = BasePriceParseConfigurationParams(
    black_list_provider=BlackListProviderForTests(),
    markup_rules_provider=MarkupRulesProviderForTests(),
    stop_words_provider=StopWordsProviderForTests(),
    vendor_list=VendorListProviderForTests(vendor_list_config),
    manufacturer_aliases=ManufacturerAliasesProviderForTests(),
    parser_params=poshk_params,
)


def get_fake_parser(parse_result: Any) -> PoshkParser:
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return PoshkParser(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


def test_parse() -> None:
    """check all field for one price-row"""

    parsed_items: List[RowItem] = get_fake_parser(poshk_one_item_result()).parse()

    assert len(parsed_items) == 1
    assert parsed_items[0].title == "10-16.5 Nortec ER-218 10PR 135B TL спецшина"
    assert parsed_items[0].type_production == "Автошина"
    assert parsed_items[0].price_markup == 6070
    assert parsed_items[0].supplier_name == "Пошк"
    assert parsed_items[0].percent_markup == 25.0


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
def test_prepare_title(title: Any, prepared_title: Any) -> None:
    """check prepare title"""

    row_item = RowItem({"title": title})
    title = PoshkParser.prepare_title(row_item.title)

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
    def test_set_category(self, title: Any, category: Any) -> None:
        """test define category name by title"""
        parse_result = poshk_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["title"] = title
        parsed_items: List[RowItem] = get_fake_parser(parse_result).parse()
        assert parsed_items[0].type_production == category

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
    def test_markup(self, price: Any, price_with_markup: Any) -> None:
        """test calculation price-markup"""
        parse_result = poshk_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["price_opt"] = price

        parser = get_fake_parser(parse_result)

        parsed_items: List[RowItem] = parser.parse()

        assert parsed_items[0].price_markup == price_with_markup

    @pytest.mark.parametrize(
        "title",
        [
            "some некондиция product",
            "some 2 сорт product",
            "185/75 R16 Forward Dinamic 156 92Q TL автопокрышка (ВОССТАНОВЛЕННАЯ), , шт",
        ],
    )
    def test_stop_words(self, title: Any) -> None:
        """test exclude price position by stop word in title"""
        parse_result = poshk_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["title"] = title

        parsed_items: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 0
