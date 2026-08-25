"""
tests for four_tochki vendor (sheet 2) after raw-parser process
"""

from typing import Any
from unittest.mock import patch

from test_parsers.fixtures.four_tochki_sheet2 import (
    four_tochki_invalid_item_result,
    four_tochki_one_item_result,
    four_tochki_one_item_result_1,
)
from test_parsers.test_vendors.parse_config import (
    MimMarkupRulesProviderForTests,
    make_parse_configuration,
)

from parsers.base_parser.base_parser import make_parser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.four_tochki.four_tochki_sheet2 import (
    FourTochkiParser2Sheet,
    fourtochki_sheet_2_params,
)

parser_config = make_parse_configuration(fourtochki_sheet_2_params, MimMarkupRulesProviderForTests())


def get_fake_parser(parse_result: Any) -> FourTochkiParser2Sheet:
    """get fake parser"""
    FakeXlsReader.parse_result = next(iter(parse_result.values()))
    return make_parser(
        FourTochkiParser2Sheet,
        ParseConfiguration(parser_config),
        file_prices=list(parse_result.keys()),
        data_reader=FakeXlsReader,
    )


def _title_parser() -> FourTochkiParser2Sheet:
    return FourTochkiParser2Sheet(parse_config=ParseConfiguration(parser_config))


def test_parse() -> None:
    """check all field for one price-row"""

    parsed_items: list[RowItem] = get_fake_parser(four_tochki_one_item_result()).parse()

    assert len(parsed_items) == 1
    assert parsed_items[0].title == "6.5x16 5x114.3 ET45 60.1 MBMF Alcasta M35"
    assert parsed_items[0].type_production == "Диск"
    assert parsed_items[0].price_markup == 8270
    assert parsed_items[0].supplier_name == "Форточки"
    assert parsed_items[0].percent_markup == 14.7

    parsed_items_alt: list[RowItem] = get_fake_parser(four_tochki_one_item_result_1()).parse()

    assert len(parsed_items_alt) == 1
    assert parsed_items_alt[0].title == "5.5x14 4x98 ET38 58.6 Алмаз Скад Ягуар (КЛ147)"
    assert parsed_items_alt[0].type_production == "Диск"
    assert parsed_items_alt[0].price_markup == 8270
    assert parsed_items_alt[0].supplier_name == "Форточки"
    assert parsed_items_alt[0].percent_markup == 14.7


def test_parse_with_invalid_item() -> None:
    """one invalid item is skipped"""

    with patch("core.log_message.log_msg") as mock_log_msg:
        parsed_items: list[RowItem] = get_fake_parser(four_tochki_invalid_item_result()).parse()
    assert len(parsed_items) == 1
    assert mock_log_msg.call_count == 2

    log_arg_value = mock_log_msg.mock_calls[0].args[0]

    assert "Не удалось разобрать строку (№ 3) у поставщика: " in log_arg_value
    assert "FourTochkiParser2Sheet" in log_arg_value
    assert "value': 'invalid value'" in log_arg_value
    assert "could not convert string to float: 'invalid value'" in log_arg_value
    assert mock_log_msg.mock_calls[0].kwargs == {"level": 40, "need_print_log": True}

    assert "Alcasta" in mock_log_msg.mock_calls[1].args[0]
    assert "WHS198858" in mock_log_msg.mock_calls[1].args[0]
    assert mock_log_msg.mock_calls[1].kwargs == {"level": 40, "need_print_log": False}


def test_prepared_title_skips_empty_parts() -> None:
    title = _title_parser().get_prepared_title(RowItem({}))
    assert "XXXX" not in title
    assert "Xxxx" not in title


def test_disk_title_keeps_thickness_and_et0() -> None:
    row = RowItem(
        {
            "title": "11,75x22,5/10x335 ET0 D281 Silver (8221107) (15,5 мм) Китай, прицеп (б/к) 5 000 кг усил.",
            "manufacturer_name": "SRW",
            "model": "10/335/281/0",
            "width": 11.75,
            "diameter": 22.5,
            "slot_count": 10,
            "pcd1": 335,
            "eet": 0,
            "central_diameter": 281,
            "color": "Silver",
        }
    )
    title = _title_parser().get_prepared_title(row)
    assert "ET0" in title
    assert "(15.5 мм)" in title
    assert "усил." in title
    assert "б/к" in title
    assert "22.5" in title
    assert "Китай" not in title
    assert "прицеп" not in title
    assert "8221107" not in title
    assert "5 000" not in title
    assert row.disk_thickness == "15.5"


def test_disk_title_tube_keeps_thickness() -> None:
    row = RowItem(
        {
            "title": "8,5x24/10x335 ET180 D281 Silver (16 мм) (под камеру)",
            "manufacturer_name": "SRW",
            "model": "10/335/281/180",
            "width": 8.5,
            "diameter": "24.0",
            "disk_thickness": "16",
            "slot_count": 10,
            "pcd1": 335,
            "eet": 180,
            "central_diameter": 281,
            "color": "Silver",
        }
    )
    title = _title_parser().get_prepared_title(row)
    assert "под камеру" in title
    assert "x24 " in title or title.startswith("8.5x24")
    assert row.disk_thickness == "16"


_ZEPP_FIELDS = {
    "manufacturer_name": "ZEPP",
    "model": "10/335/281/175",
    "width": 9.0,
    "diameter": 22.5,
    "slot_count": 10,
    "pcd1": 335,
    "eet": 175,
    "central_diameter": 281,
    "color": "Sil",
}
_ZEPP_CANON = "9.0x22.5 10x335 ET175 281 Sil Zepp 10/335/281/175 (16 мм) б/к"


def _zepp_row(name: str) -> RowItem:
    return RowItem({"title": name, **_ZEPP_FIELDS})


def test_zepp_factory_and_valve_titles_differ() -> None:
    yz = _title_parser().get_prepared_title(
        _zepp_row("9,0x22,5/10x335 ET175 D281 Sil (YZ) (16 мм) (б/к)"),
    )
    hap_outer = _title_parser().get_prepared_title(
        _zepp_row("9,0x22,5/10x335 ET175 D281 Sil (HAP) alive (16 мм) (б/к) наруж. вентиль"),
    )
    hap_inner = _title_parser().get_prepared_title(
        _zepp_row("9,0x22,5/10x335 ET175 D281 Sil (HAP) (16 мм) (б/к) внутр. вентиль"),
    )
    assert yz == f"{_ZEPP_CANON} (YZ)"
    assert hap_outer == f"{_ZEPP_CANON} (HAP) alive наруж. вентиль"
    assert hap_inner == f"{_ZEPP_CANON} (HAP) внутр. вентиль"
    assert len({yz, hap_outer, hap_inner}) == 3


def test_disk_title_keeps_other_truck_tails() -> None:
    name = (
        "9,0x22,5/10x335 ET175 D281 Sil (JNTS) (5221105) (16 мм) (б/к) "
        "под футорку с вент. (кольцо) Китай, прицеп 4 500 кг"
    )
    title = _title_parser().get_prepared_title(_zepp_row(name))
    assert title == f"{_ZEPP_CANON} (JNTS) под футорку с вент. (кольцо)"
    assert "5221105" not in title
    assert "Китай" not in title
    assert "4 500" not in title
