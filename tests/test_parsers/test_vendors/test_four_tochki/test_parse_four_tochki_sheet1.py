"""
tests for four_tochki vendor (sheet 1) after raw-parser process
"""

from typing import Any, List

import pytest
from test_parsers.fixtures.four_tochki_sheet1 import (
    four_tochki_many_item_result,
    four_tochki_one_item_result,
)
from test_parsers.test_vendors.parse_config import (
    MimMarkupRulesProviderForTests,
    make_parse_configuration,
)

from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.four_tochki.four_tochki_sheet1 import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_params,
)

parser_config = make_parse_configuration(fourtochki_sheet_1_params, MimMarkupRulesProviderForTests())


def get_fake_parser(parse_result: Any) -> FourTochkiParser1Sheet:
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return FourTochkiParser1Sheet(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


def test_parse() -> None:
    """check all field for one price-row"""

    parsed_items: List[RowItem] = get_fake_parser(four_tochki_many_item_result()).parse()

    assert len(parsed_items) == 3
    assert parsed_items[0].title == "205/55R16 BF Goodrich Advantage 94W"
    assert parsed_items[0].type_production == "Легковая шина"
    assert parsed_items[0].price_markup == 7340
    assert parsed_items[0].supplier_name == "Форточки"
    assert parsed_items[0].percent_markup == 27.17

    # метрический размер
    assert parsed_items[1].title == "31x10.5R15 BF Goodrich All Terrain T/A KO2 109S LT"
    assert parsed_items[1].price_markup == 24870
    assert parsed_items[1].percent_markup == 27.04

    # грузовая шина
    assert parsed_items[2].title == "235/75R17.5 BF Goodrich Route Control D 132/130M"
    assert parsed_items[2].type_production == "Грузовая шина"


def test_replace_diameter() -> None:
    """check replace RZ -> ZR"""

    parsed_items: List[RowItem] = get_fake_parser(four_tochki_one_item_result(diameter="RZ16")).parse()

    assert len(parsed_items) == 1
    assert parsed_items[0].title == "205/55ZR16 BF Goodrich Advantage 94W"
    assert parsed_items[0].type_production == "Легковая шина"
    assert parsed_items[0].price_markup == 7340
    assert parsed_items[0].supplier_name == "Форточки"
    assert parsed_items[0].percent_markup == 27.17


def test_prepare_title_replace_999() -> None:
    """999 -> L"""

    row = RowItem(
        {
            RowItem.height_percent.name: "999",
            RowItem.width.name: "11",
            RowItem.diameter.name: "--20",
        }
    )

    prepared_title = FourTochkiParser1Sheet.get_prepared_title(row)
    assert prepared_title == "11L-20"


def test_prepare_title_width_two_zero() -> None:
    """10.00-20 Armour TI300 16PR TTF"""

    row = RowItem(
        {
            RowItem.width.name: 10,
            RowItem.diameter.name: "--20",
            RowItem.manufacturer.name: "Armour",
            RowItem.model.name: "TI300",
            RowItem.layering.name: "16PR",
            RowItem.camera_type.name: "TTF",
        }
    )

    prepared_title = FourTochkiParser1Sheet.get_prepared_title(row)
    assert prepared_title == "10.00-20 Armour TI300 16PR TTF"


def test_prepare_title_width_one_zero() -> None:
    """10.0/75-15.3 Forerunner QH602 R-4 12PR TL"""

    row = RowItem(
        {
            RowItem.width.name: 10,
            RowItem.height_percent.name: 75,
            RowItem.diameter.name: "--15.3",
            RowItem.manufacturer.name: "Forerunner",
            RowItem.model.name: "QH602 R-4",
            RowItem.layering.name: "12PR",
            RowItem.camera_type.name: "TL",
            RowItem.tire_type.name: "Спецтехника",
        }
    )

    prepared_title = FourTochkiParser1Sheet.get_prepared_title(row)
    assert prepared_title == "10.0/75-15.3 Forerunner QH602 R-4 12PR TL"


def test_prepare_title_width_1() -> None:
    """11L-15 Galaxy Rib Implement I-1 12PR TL"""

    row = RowItem(
        {
            RowItem.width.name: "11",
            RowItem.height_percent.name: "999",
            RowItem.diameter.name: "--15",
            RowItem.manufacturer.name: "Galaxy",
            RowItem.model.name: "Rib Implement I-1",
            RowItem.layering.name: "12PR",
            RowItem.camera_type.name: "TL",
            RowItem.tire_type.name: "Спецтехника",
        }
    )

    prepared_title = FourTochkiParser1Sheet.get_prepared_title(row)
    assert prepared_title == "11L-15 Galaxy Rib Implement I-1 12PR TL"


def test_prepare_title_1() -> None:
    """..."""

    row = RowItem(
        {
            RowItem.width.name: "12.5",
            RowItem.height_percent.name: 80,
            RowItem.diameter.name: "--18",
            RowItem.manufacturer.name: "Armour",
            RowItem.model.name: "L-5B",
            RowItem.layering.name: "16",
            RowItem.camera_type.name: "TL",
            RowItem.tire_type.name: "Спецтехника",
        }
    )

    prepared_title = FourTochkiParser1Sheet.get_prepared_title(row)
    assert prepared_title == "12.5/80-18 Armour L-5B 16 TL"


@pytest.mark.parametrize(
    ("tire_type", "expected"),
    [
        ("грузовая", "Грузовая шина"),
        ("  ГРУЗОВАЯ  ", "Грузовая шина"),
        ("легковая", "Легковая шина"),
        ("спецтехника", "Спецшина"),
        ("мото", "Мотошина"),
        ("unknown", "Автошина"),
    ],
)
def test_current_category_by_tire_type(tire_type: str, expected: str) -> None:
    row = RowItem({RowItem.tire_type.name: tire_type})
    assert FourTochkiParser1Sheet.get_current_category(row) == expected
