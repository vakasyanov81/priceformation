"""tests for four_tochki title helpers."""

from typing import Any

import pytest

from parsers.row_item.row_item import RowItem
from parsers.vendors.four_tochki.four_tochki_title import (
    get_prepared_title,
    is_special_tire,
    is_truck_tire,
)
from parsers.vendors.four_tochki.four_tochki_title_parts import (
    default_tire_title,
    ext_diameter_title,
    truck_title,
)

_PARTS = ("205", "/55", "", "R16")
_WRAP = "XXXX"
_TRUCK = "грузовая"


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


def test_truck_title_keeps_camera_and_sidewall() -> None:
    row = RowItem(
        {
            "model": "TRD06",
            "layering": "20",
            "camera_type": "TL",
            "inscription_on_the_side": "3PMSF",
            "index_load": "157/154",
            "index_velocity": "K",
        }
    )
    title = truck_title(row, ("315", "/80", "", "R22.5"), "Triangle")
    assert title == "315/80R22.5 Triangle TRD06 20 TL 3PMSF 157/154K"


def test_default_title_includes_runflat() -> None:
    row = RowItem(
        {
            "model": "Scorpion Verde All-Season",
            "camera_type": "TL",
            "index_load": "103",
            "index_velocity": "H",
            "run_flat": "Да",
        }
    )
    title = default_tire_title(row, ("235", "/60", "", "R18"), "Pirelli")
    assert title == "235/60R18 Pirelli Scorpion Verde All-Season TL 103H RunFlat"


def test_ext_diameter_title_skips_empty_optional() -> None:
    row = RowItem({"ext_diameter": 31})
    assert _WRAP not in ext_diameter_title(row, _PARTS, "Kama")


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        ({"width": "205", "diameter": "R18"}, "205R18"),
        ({"width": "11", "diameter": "R20"}, "11R20"),
        ({"width": "10", "diameter": "R18"}, "10R18"),
        ({"width": "11", "diameter": "R20", "tire_type": _TRUCK}, "11.00R20"),
        ({"width": "315", "diameter": "R22.5", "tire_type": _TRUCK}, "315R22.5"),
        ({"width": "11", "diameter": "R16", "tire_type": _TRUCK}, "11R16"),
    ],
)
def test_prepared_title_width_postfix(fields: dict[str, Any], expected: str) -> None:
    assert get_prepared_title(RowItem(fields)) == expected
