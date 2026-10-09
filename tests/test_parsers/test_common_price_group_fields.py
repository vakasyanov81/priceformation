"""tests for grouping field helpers."""

from typing import Any

import pytest

from domain.row_item.row_item import RowItem
from parsers.common_price_group_fields import (
    brand_key_parts,
    camera_from_field,
    camera_key,
    disk_extras_key,
    sidewall,
    yes_flag,
)

_BRAND_ALIASES: dict[str, Any] = {'Cordiant': {'group': 'kordiant', 'aliases': []}}


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('да', 'да'),
        ('ДА', 'да'),
        ('yes', 'да'),
        ('YES', 'да'),
        ('1', 'да'),
        ('true', 'да'),
        ('TRUE', 'да'),
        ('runflat', 'да'),
        ('RunFlat', 'да'),
        (None, ''),
        ('', ''),
        ('no', ''),
        ('нет', ''),
    ],
)
def test_yes_flag(raw: Any, expected: str) -> None:
    assert yes_flag(raw) == expected


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('tt', 'TT'),
        ('TT', 'TT'),
        ('ttf', 'TTF'),
        ('TTF', 'TTF'),
        ('TT (только шина)', 'TT-ONLY'),
        ('только шина', 'TT-ONLY'),
        ('tl', None),
        ('TL', None),
        ('', None),
        (None, None),
    ],
)
def test_camera_from_field(raw: Any, expected: str | None) -> None:
    assert camera_from_field(raw) == expected


def test_camera_key_prefers_field_over_intimacy() -> None:
    row = RowItem({'camera_type': 'tt'})
    assert camera_key(row, 'TL') == 'TT'


def test_camera_key_from_intimacy_token() -> None:
    row = RowItem({})
    assert camera_key(row, 'tt') == 'TT'
    assert camera_key(row, 'TL') is None


def test_sidewall_lowercases() -> None:
    assert sidewall('M+S') == 'm+s'
    assert sidewall('3PMSF') == '3pmsf'
    assert sidewall(None) == ''


def _brand_row(manufacturer: str | None, brand: str | None) -> RowItem:
    return RowItem({'manufacturer_name': manufacturer, 'brand': brand})


@pytest.mark.parametrize(
    ('manufacturer', 'brand', 'expected'),
    [
        ('KAMA', 'KAMA', ('kama', '', 'kama', '')),
        ('KAMA', 'Cordiant', ('kama', 'cordiant', 'kama', 'cordiant')),
        (None, 'Cordiant', ('', 'cordiant', '', 'cordiant')),
        (None, None, ('', '', '', '')),
    ],
)
def test_brand_key_parts_normalizes_and_hides_own_brand(
    manufacturer: str | None,
    brand: str | None,
    expected: tuple[str, str, str, str],
) -> None:
    """Регистр и пустые поля: части ключа в нижнем регистре, совпавший бренд пуст."""
    assert brand_key_parts(_brand_row(manufacturer, brand), {}) == expected


def test_brand_key_parts_hides_brand_of_same_group() -> None:
    """Бренд, попадающий в ту же группу, что производитель, в ключ не идёт."""
    assert brand_key_parts(_brand_row('Cordiant', 'Cordiant'), _BRAND_ALIASES) == ('cordiant', '', 'kordiant', '')


def test_disk_extras_key_lowercases_title_extras() -> None:
    """Хвосты диска (завод/вентиль) в ключе — в нижнем регистре."""
    row = RowItem({'type_production': 'диск', 'title': '5.5x14 Скад (HAP) наруж. вентиль'})
    assert disk_extras_key(row) == '(hap) наруж. вентиль'


def test_disk_extras_key_empty_for_non_disk() -> None:
    row = RowItem({'type_production': 'легковая', 'title': '5.5x14 Скад (HAP)'})
    assert disk_extras_key(row) == ''


def test_disk_extras_key_empty_without_extras() -> None:
    row = RowItem({'type_production': 'диск', 'title': '5.5x14 Скад Ягуар'})
    assert disk_extras_key(row) == ''
