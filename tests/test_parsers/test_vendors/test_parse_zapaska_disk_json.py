"""
tests for zapaska vendor after raw-parser process
"""

__author__ = "Kasyanov V.A."

from typing import List

import pytest

from src.parsers.base_parser.base_parser_config import (
    ParseConfiguration,
)
from src.parsers.row_item.row_item import RowItem
from src.parsers.vendors.zapaska_disk_json import zapaska_params
from src.parsers.vendors.zapaska_disk_json import ZapaskaDiskJSON
from tests.test_parsers.test_vendors.parse_config import make_parse_configuration

parser_config = make_parse_configuration(zapaska_params)


def get_fake_parser(file_prices: list[str]):
    """get fake parser"""
    return ZapaskaDiskJSON(
        file_prices=file_prices,
        parse_config=ParseConfiguration(parser_config),
    )


class TestParseZapaskaDiskJSON:
    """
    tests for Poshk vendor after raw-parser process
    """

    def _test_parse(self):
        """check all field for one price-row"""

        result: List[RowItem] = get_fake_parser(
            ["/home/huck/petprojects/priceformation/tests/test_parsers/fixtures/zapaska_disk.json"]
        ).parse()

        res = result[0]

        assert len(result) == 1
        assert res.title == "Replay HND369 7.5*20 5*114.3 ET49.5 D67.1 MGMF"
        assert res.price_markup == 4900
        assert res.price_recommended == 4201
        assert res.supplier_name == "Запаска (остатки)"
        assert res.percent_markup == 22.12
