"""tests for shared nomenclature title composition."""

from typing import Any

import pytest

from parsers.nomenclature_title import (
    brand_label,
    compose_tire_title,
    join_size_parts,
    join_title_parts,
    load_velocity,
)
from parsers.row_item.row_item import RowItem


def _row(**fields: Any) -> RowItem:
    return RowItem(fields)


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        (("205/55R16", "Kama", "Euro"), "205/55R16 Kama Euro"),
        (("205/55R16", "", "Euro"), "205/55R16 Euro"),
        (("205/55R16", None, "  "), "205/55R16"),
    ],
)
def test_join_title_parts_skips_empty(parts: tuple[object, ...], expected: str) -> None:
    assert join_title_parts(*parts) == expected


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        (("205", "/55", "R16"), "205/55R16"),
        (("30", "x", "9.5", "R", "15"), "30x9.5R15"),
        (("30", "/", "", "R", "15"), "30/R15"),
        (("11", ".00", "", "R20"), "11.00R20"),
    ],
)
def test_join_size_parts_skips_empty(parts: tuple[object, ...], expected: str) -> None:
    assert join_size_parts(*parts) == expected


def test_brand_label_capitalizes() -> None:
    assert brand_label(_row(manufacturer_name="KAMA")) == "Kama"
    assert brand_label(_row()) == ""


def test_load_velocity_concatenates() -> None:
    assert load_velocity(_row(index_load="94", index_velocity="W")) == "94W"
    assert load_velocity(_row(index_load="94")) == "94"
    assert load_velocity(_row()) == ""


def test_compose_tire_title_order_and_extras() -> None:
    row = _row(manufacturer_name="pirelli", model="P Zero", layering="XL")
    title = compose_tire_title(row, "235/40R18", row.layering, "103Y")
    assert title == "235/40R18 Pirelli P Zero XL 103Y"
