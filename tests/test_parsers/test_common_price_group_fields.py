"""tests for grouping field helpers."""

from typing import Any

import pytest

from parsers.common_price_group_fields import camera_from_field, camera_key, sidewall, yes_flag
from parsers.row_item.row_item import RowItem


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("да", "да"),
        ("ДА", "да"),
        ("yes", "да"),
        ("YES", "да"),
        ("1", "да"),
        ("true", "да"),
        ("TRUE", "да"),
        ("runflat", "да"),
        ("RunFlat", "да"),
        (None, ""),
        ("", ""),
        ("no", ""),
        ("нет", ""),
    ],
)
def test_yes_flag(raw: Any, expected: str) -> None:
    assert yes_flag(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("tt", "TT"),
        ("TT", "TT"),
        ("ttf", "TTF"),
        ("TTF", "TTF"),
        ("TT (только шина)", "TT-ONLY"),
        ("только шина", "TT-ONLY"),
        ("tl", None),
        ("TL", None),
        ("", None),
        (None, None),
    ],
)
def test_camera_from_field(raw: Any, expected: str | None) -> None:
    assert camera_from_field(raw) == expected


def test_camera_key_prefers_field_over_intimacy() -> None:
    row = RowItem({"camera_type": "tt"})
    assert camera_key(row, "TL") == "TT"


def test_camera_key_from_intimacy_token() -> None:
    row = RowItem({})
    assert camera_key(row, "tt") == "TT"
    assert camera_key(row, "TL") is None


def test_sidewall_lowercases() -> None:
    assert sidewall("M+S") == "m+s"
    assert sidewall("3PMSF") == "3pmsf"
    assert sidewall(None) == ""
