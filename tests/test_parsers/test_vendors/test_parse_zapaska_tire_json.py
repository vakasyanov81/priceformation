"""
tests for zapaska (json) tire vendor after raw-parser process
"""

import json
from pathlib import Path
from typing import Any
from unittest import skip

import pytest
from test_parsers.test_vendors.parse_config import make_parse_configuration

from cfg.main import get_config
from parsers.base_parser.base_parser import make_parser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_tire_json import ZapaskaTireJSON, zapaska_tire_params

_FIXTURE_TIRE = "tests/test_parsers/fixtures/zapaska_tire.json"

parser_config = make_parse_configuration(zapaska_tire_params)


def get_fake_parser(file_prices: list[str]) -> ZapaskaTireJSON:
    """get fake parser"""
    return make_parser(
        ZapaskaTireJSON,
        ParseConfiguration(parser_config),
        file_prices=file_prices,
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

    def test_parse(self) -> None:
        """check all field for one price-row"""

        root = get_config()().project_root
        parser = get_fake_parser([f"{root}/{_FIXTURE_TIRE}"])
        parsed_items: list[RowItem] = parser.parse()

        res = parsed_items[0]

        assert len(parsed_items) == 1
        assert res.title == "315/80R22.5 Three-A T276+ 20PR 157/154M TL"
        assert res.price_markup == 25830.0
        assert res.price_recommended == 24670.0
        assert res.supplier_name == "Запаска (шины)"
        assert res.percent_markup == 12.04
        assert res.season == "Летняя"
        assert res.type_production == "Грузовая шина"

    def test_unknown_category_is_skipped(self, tmp_path: Path) -> None:
        """неизвестная категория поставщика не попадает в прайс"""
        root = get_config()().project_root
        rows = json.loads((Path(root) / _FIXTURE_TIRE).read_text(encoding="utf-8"))
        rows[0]["category"] = "SUV"
        price_file = tmp_path / "tire.json"
        price_file.write_text(json.dumps(rows), encoding="utf-8")

        parser = get_fake_parser([str(price_file)])
        parsed_items: list[RowItem] = parser.parse()

        assert parsed_items == []
        assert parser.unknown_category_skips == ["SUV"]

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
    @skip("markup parametrize not ready")
    def test_markup(self, prices: Any) -> None:
        """test calculation price-markup"""
        _price_opt, _price_recommended, price_markup = prices
        root = get_config()().project_root
        parser = get_fake_parser([f"{root}/{_FIXTURE_TIRE}"])
        parsed_items: list[RowItem] = parser.parse()
        assert parsed_items[0].price_markup == price_markup
