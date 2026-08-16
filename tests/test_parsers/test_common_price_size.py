"""tests for size canon used in grouping key."""

from typing import Any

import pytest

from parsers.common_price_size import canon_number, size_fields
from parsers.row_item.row_item import RowItem


def _row(**fields: Any) -> RowItem:
    payload: dict[str, Any] = {"title": "", "width": "", "diameter": ""}
    payload.update(fields)
    return RowItem(payload)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, ""),
        ("", ""),
        ("  ", ""),
        ("22,5", "22.5"),
        ("22.5", "22.5"),
        ("22,50", "22.5"),
        ("12.50", "12.5"),
        ("16", "16"),
        ("R16", "R16"),
    ],
)
def test_canon_number(raw: Any, expected: str) -> None:
    assert canon_number(raw) == expected


def test_size_fields_comma_diameter_matches_dot() -> None:
    assert size_fields(_row(diameter="22,5")) == size_fields(_row(diameter="22.5"))


def test_size_fields_inch_outer_from_title() -> None:
    item_35 = _row(title="35X12.50R17 Maxxis", width="12.50", diameter="17")
    item_33 = _row(title="33X12.50R17 Maxxis", width="12.50", diameter="17")
    assert size_fields(item_35) != size_fields(item_33)
    assert size_fields(item_35)[2] == "35"
    assert size_fields(item_33)[2] == "33"


def test_size_fields_inch_lt_matches_ext_field() -> None:
    from_title = _row(title="35x12.50R17LT Maxxis")
    from_field = _row(title="Maxxis", width="12.5", diameter="17", ext_diameter=35)
    assert size_fields(from_title) == size_fields(from_field) == ("12.5", "17", "35")


def test_size_fields_cyrillic_x_and_comma() -> None:
    assert size_fields(_row(title="35х12,50R17")) == ("12.5", "17", "35")
