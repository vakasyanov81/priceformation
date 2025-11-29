"""
tests for zapaska (json) tire vendor after raw-parser process
"""

__author__ = "Kasyanov V.A."

from typing import List
from unittest import skip

import pytest

from cfg.main import get_config
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_tire_json import ZapaskaTireJSON, zapaska_tire_params
from test_parsers.test_vendors.parse_config import make_parse_configuration

parser_config = make_parse_configuration(zapaska_tire_params)


def get_fake_parser(file_prices: list[str]):
    """get fake parser"""
    return ZapaskaTireJSON(
        file_prices=file_prices,
        parse_config=ParseConfiguration(parser_config),
    )


class TestParseZapaskaTireJSON:
    """
    tests for zapaska (json) tire vendor after raw-parser process

    [{
    "cae": "КА-00057379",
    "price": "23055",
    "retail": "24670",
    "rest": 12,
    "brand": "Three-A",
    "category": "Грузовая",
    "season": "лето",
    "width": "315",
    "height": "80",
    "diameter": "22.5",
    "load_index": "157/154",
    "speed_index": "M",
    "model": "T276+",
    "name": "315/80R22.5    THREE-A T276+  20PR 157/154M TL",
    "article": "380S0092"
    }]
    """

    def test_parse(self):
        """check all field for one price-row"""

        root = get_config()().project_root
        obj = get_fake_parser([f"{root}/tests/test_parsers/fixtures/zapaska_tire.json"])
        result: List[RowItem] = obj.parse()

        res = result[0]

        assert len(result) == 1
        # assert res.title == "315/80R22.5 Three-A T276+ 157/154M"
        assert res.title == "315/80R22.5 Three-A T276+ 20PR 157/154M TL"
        assert res.price_markup == 25830.0
        assert res.price_recommended == 24670.0
        assert res.supplier_name == "Запаска (шины)"
        assert res.percent_markup == 12.04
        assert res.season == "Летняя"

    @pytest.mark.parametrize(
        "prices",
        [
            (100, 400, 400),
            (1000, 1100, 1150),
            (10000, 11000, 11000),
            (20000, 20020, 22410),
            (20000, 25000, 25000),
            (60000, 60100, 67200),
        ],
    )
    @skip
    def test_markup(self, prices):
        """test calculation price-markup"""
        price_opt, price_recommended, price_markup = prices
        root = get_config()().project_root
        obj = get_fake_parser([f"{root}/tests/test_parsers/fixtures/zapaska_tire.json"])
        result: List[RowItem] = obj.parse()
        assert result[0].price_markup == price_markup

    @classmethod
    def get_first_row_item(cls, parse_result) -> RowItem:
        """get first item from parse result"""
        file = list(parse_result.keys())[0]
        return RowItem(parse_result[file][0])
