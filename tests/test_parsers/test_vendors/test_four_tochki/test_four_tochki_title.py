"""tests for four_tochki title helpers."""

from parsers.row_item.row_item import RowItem
from parsers.vendors.four_tochki.four_tochki_title import is_special_tire, is_truck_tire
from parsers.vendors.four_tochki.four_tochki_title_parts import ext_diameter_title, truck_title

_PARTS = ("205", "/55", "", "R16")
_WRAP = "XXXX"


def test_truck_tire_by_type() -> None:
    assert is_truck_tire(RowItem({"tire_type": "грузовая"})) is True
    assert is_truck_tire(RowItem({"tire_type": "ГРУЗОВАЯ"})) is True
    assert is_truck_tire(RowItem({"tire_type": "легковая"})) is False
    assert is_truck_tire(RowItem({})) is False


def test_special_tire_empty_is_false() -> None:
    assert is_special_tire(RowItem({})) is False
    assert is_special_tire(RowItem({"tire_type": "спецтехника"})) is True


def test_truck_title_skips_empty_model() -> None:
    assert _WRAP not in truck_title(RowItem({}), _PARTS, "Kama")


def test_ext_diameter_title_skips_empty_optional() -> None:
    row = RowItem({"ext_diameter": 31})
    assert _WRAP not in ext_diameter_title(row, _PARTS, "Kama")
