"""tests for four_tochki disk title helpers."""

import pytest

from parsers.vendors.four_tochki.four_tochki_disk_title import disk_diameter, et_label


def test_et_label_none_and_empty() -> None:
    assert et_label(None) == 'ET'
    assert et_label('') == 'ET'


def test_four_tochki_base_raises_not_implemented() -> None:
    """FourTochkiParserBase.get_current_category — абстрактный метод."""
    from parsers.row_item.row_item import RowItem
    from parsers.vendors.four_tochki.four_tochki_base import FourTochkiParserBase

    with pytest.raises(NotImplementedError):
        FourTochkiParserBase.get_current_category(RowItem({}))


def test_mim_base_raises_not_implemented() -> None:
    """MimParserBase.get_current_category — абстрактный метод."""
    from parsers.vendors.mim.mim_base import MimParserBase

    with pytest.raises(NotImplementedError):
        MimParserBase.get_current_category()


def test_mim_3sheet_category_returns_disk() -> None:
    """MimParser3Sheet.get_current_category возвращает 'Диск'."""
    from parsers.vendors.mim.mim_3sheet import MimParser3Sheet

    assert MimParser3Sheet.get_current_category() == 'Диск'


def test_disk_diameter_strips_dot_zero() -> None:
    assert disk_diameter('8.0') == '8'
    assert disk_diameter(8.0) == '8'


def test_disk_diameter_keeps_fraction() -> None:
    assert disk_diameter('22.5') == '22.5'
    assert disk_diameter('16.0') == '16'
