"""
tests for zapaska vendor after raw-parser process
"""

from typing import List

from cfg.main import get_config
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_disk_json import zapaska_params
from parsers.vendors.zapaska_disk_json import ZapaskaDiskJSON
from test_parsers.test_vendors.parse_config import make_parse_configuration

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

    def test_parse(self):
        """check all field for one price-row"""

        root = get_config()().project_root
        result: List[RowItem] = get_fake_parser([f"{root}/tests/test_parsers/fixtures/zapaska_disk.json"]).parse()

        res = result[0]

        assert len(result) == 1
        # assert res.title == "Replay HND369 7.5*20 5*114.3 ET49.5 D67.1 MGMF"
        assert res.title == "20 Replay HND369 7.5*20 5*114.3 ET49.5 D67.1 MGMF"
        # assert res.price_markup == 28750.0
        assert res.price_markup == 29500.0
        assert res.price_recommended == 29500.0
        assert res.supplier_name == "Запаска (диски)"
        # assert res.percent_markup == 12.02
        assert res.percent_markup == 14.94
