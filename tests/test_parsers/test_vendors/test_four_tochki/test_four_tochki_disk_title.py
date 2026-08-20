"""tests for four_tochki disk title helpers."""

from parsers.vendors.four_tochki.four_tochki_disk_title import disk_diameter, et_label


def test_et_label_none_and_empty() -> None:
    assert et_label(None) == "ET"
    assert et_label("") == "ET"


def test_et_label_keeps_zero() -> None:
    assert et_label(0) == "ET0"
    assert et_label("0") == "ET0"


def test_disk_diameter_strips_dot_zero() -> None:
    assert disk_diameter("8.0") == "8"
    assert disk_diameter(8.0) == "8"


def test_disk_diameter_keeps_fraction() -> None:
    assert disk_diameter("22.5") == "22.5"
    assert disk_diameter("16.0") == "16"
