"""
tests for zapaska vendor after raw-parser process
"""

from test_parsers.test_vendors.parse_config import ZapaskaMarkupRulesProviderForTests, make_parse_configuration

from cfg.main import get_config
from parsers.base_parser.base_parser import make_parser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_disk_json import ZapaskaDiskJSON, zapaska_params

_NO_RRC_OPT = 10000
_NO_RRC_MARKUP = 11600

parser_config = make_parse_configuration(zapaska_params, markup_rules=ZapaskaMarkupRulesProviderForTests())


def get_fake_parser(file_prices: list[str]) -> ZapaskaDiskJSON:
    """get fake parser"""
    return make_parser(
        ZapaskaDiskJSON,
        ParseConfiguration(parser_config),
        file_prices=file_prices,
    )


class TestParseZapaskaDiskJSON:
    """
    tests for Poshk vendor after raw-parser process
    """

    def test_parse(self) -> None:
        """check all field for one price-row"""

        root = get_config()().project_root
        parsed_items: list[RowItem] = get_fake_parser([f"{root}/tests/test_parsers/fixtures/zapaska_disk.json"]).parse()

        res = parsed_items[0]

        assert len(parsed_items) == 1
        assert res.title == "20 Replay HND369 7.5*20 5*114.3 ET49.5 D67.1 MGMF"
        assert res.price_markup == 29500.0
        assert res.price_recommended == 29500.0
        assert res.supplier_name == "Запаска (диски)"
        assert res.pcd1 == 114.3
        assert res.percent_markup == 14.94


def test_markup_without_recommended() -> None:
    parser = get_fake_parser([])
    row = RowItem({"price_opt": _NO_RRC_OPT, "title": "No retail"})
    parser.add_price_markup(row)
    assert parser.not_matched_position == ["No retail"]
    assert row.price_markup == _NO_RRC_MARKUP
