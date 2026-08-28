"""
tests for zapaska vendor after raw-parser process
"""

import pytest
from test_parsers.test_vendors.parse_config import ZapaskaMarkupRulesProviderForTests, make_parse_configuration

from cfg.main import get_config
from parsers.base_parser.base_parser import make_parser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
)
from parsers.fake_json_reader import FakeJsonPriceReader
from parsers.json_reader import JsonPriceReader
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


def test_make_parser_uses_json_price_reader() -> None:
    parser = get_fake_parser([])
    assert parser.data_reader is JsonPriceReader


def test_parse_with_fake_json_reader_without_disk(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        FakeJsonPriceReader,
        "raw_rows",
        [
            {
                "cae": "1",
                "price": 10000,
                "retail": 12000,
                "rest": 10,
                "name": "Replay HND",
                "brand": "Replay",
            },
        ],
    )
    parser = make_parser(
        ZapaskaDiskJSON,
        ParseConfiguration(parser_config),
        file_prices=["memory.json"],
        data_reader=FakeJsonPriceReader,
    )
    parsed_items = parser.parse()
    assert len(parsed_items) == 1
    assert parsed_items[0].code_art == "1"
    assert parsed_items[0].price_opt == 10000
    assert parsed_items[0].title == "Replay HND"


def test_markup_without_recommended() -> None:
    parser = get_fake_parser([])
    row = RowItem({"price_opt": _NO_RRC_OPT, "title": "No retail"})
    parser.add_price_markup(row)
    assert parser.not_matched_position == ["No retail"]
    assert row.price_markup == _NO_RRC_MARKUP


def test_prepared_title_collapses_spaces(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "parsers.vendors.zapaska_disk_json.load_title_aliases",
        lambda _name: {},
    )
    parser = get_fake_parser([])
    assert parser.get_prepared_title(RowItem({"title": "Replay   HND"})) == "Replay HND"


def test_prepared_title_applies_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "parsers.vendors.zapaska_disk_json.load_title_aliases",
        lambda _name: {"Replay HND": "Replay Honda"},
    )
    parser = get_fake_parser([])
    assert parser.get_prepared_title(RowItem({"title": "Replay  HND"})) == "Replay Honda"


def test_prepared_title_replaces_comma_in_size(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "parsers.vendors.zapaska_disk_json.load_title_aliases",
        lambda _name: {},
    )
    parser = get_fake_parser([])
    row = RowItem({"title": "31x10,50R15 Mazzini Giantsaver 109S"})
    assert parser.get_prepared_title(row) == "31x10.50R15 Mazzini Giantsaver 109S"
