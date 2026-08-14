"""tests for price grouping key helpers."""

from typing import Any

import pytest

from parsers.common_price_group_key import clear_model, define_intimacy, group_key, sanitize_value
from parsers.row_item.row_item import RowItem


def _row(**fields: Any) -> RowItem:
    payload: dict[str, Any] = {
        "title": "no marker",
        "type_production": "легковая",
        "diameter": "16",
    }
    payload.update(fields)
    return RowItem(payload)


def test_sanitize_none() -> None:
    assert sanitize_value([None, 1]) == ("", "1")


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (None, ""),
        ("", ""),
        ("КАМА-NU 701", "NU701"),
        ("NU701", "NU701"),
        ("A-B-C", "B"),
    ],
)
def test_clear_model(model: str | None, expected: str) -> None:
    assert clear_model(model) == expected


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("tyre TL extra", "TL"),
        ("tyre tt extra", "TT"),
        ("tyre TTF extra", "TTF"),
    ],
)
def test_intimacy_from_title_word(title: str, expected: str) -> None:
    assert define_intimacy(_row(title=title)) == expected


def test_intimacy_requires_separate_word() -> None:
    assert define_intimacy(_row(title="TLextra")) is None


def test_intimacy_truck_float_diameter() -> None:
    row = _row(type_production="грузовая", diameter="22.5")
    assert define_intimacy(row) == "TL"


def test_intimacy_truck_comma_diameter() -> None:
    row = _row(type_production="грузовая", diameter="22,5")
    assert define_intimacy(row) == "TL"


def test_intimacy_truck_integer_diameter() -> None:
    row = _row(type_production="грузовая", diameter="22")
    assert define_intimacy(row) is None


def test_intimacy_not_truck_float_diameter() -> None:
    row = _row(type_production="легковая", diameter="22.5")
    assert define_intimacy(row) is None


def test_intimacy_invalid_diameter() -> None:
    row = _row(type_production="грузовая", diameter="xx")
    assert define_intimacy(row) is None


def test_group_key_hides_matching_brand() -> None:
    shared = {"manufacturer_name": "НКШЗ", "model": "X"}
    same_brand = RowItem({**shared, "brand": "НКШЗ"})
    blank_brand = RowItem(shared)
    other_brand = RowItem({**shared, "brand": "Other"})

    assert group_key(same_brand) == group_key(blank_brand)
    assert group_key(same_brand) != group_key(other_brand)


def test_group_key_empty_manufacturer_and_type() -> None:
    key = group_key(_row(manufacturer_name="", type_production=""))
    assert "xxxx" not in key


def test_group_key_type_production_lower() -> None:
    key = group_key(_row(type_production="Легковая"))
    assert "легковая" in key
    assert "ЛЕГКОВАЯ" not in key


def test_group_key_uses_row_intimacy() -> None:
    assert "TL" in group_key(_row(intimacy="TL"))


def test_group_key_includes_cleared_model() -> None:
    assert "NU701" in group_key(_row(model="КАМА-NU 701"))
