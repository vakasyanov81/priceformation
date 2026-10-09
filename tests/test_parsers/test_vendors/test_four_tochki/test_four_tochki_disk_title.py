"""tests for four_tochki disk title helpers."""

from domain.row_item.row_item import RowItem
from parsers.strategies._four_tochki_disk_helper import (
    disk_diameter,
    disk_name_suffix,
    et_label,
    fill_disk_thickness,
    thickness_from_name,
)


def test_et_label_none_and_empty() -> None:
    assert et_label(None) == 'ET'
    assert et_label('') == 'ET'


def test_et_label_literal_marker_is_value() -> None:
    """Заглушка 'XXXX' — обычное значение, а не пустое."""
    assert et_label('XXXX') == 'ETXXXX'


def test_disk_diameter_strips_dot_zero() -> None:
    assert disk_diameter('8.0') == '8'
    assert disk_diameter(8.0) == '8'


def test_disk_diameter_keeps_fraction() -> None:
    assert disk_diameter('22.5') == '22.5'
    assert disk_diameter('16.0') == '16'


def test_disk_diameter_empty_is_empty() -> None:
    """Пустой или None диаметр не подменяется заглушкой."""
    assert disk_diameter(None) == ''
    assert disk_diameter('') == ''


def test_disk_name_suffix_full() -> None:
    """Толщина, усиление и камерность собираются в хвост диска."""
    assert disk_name_suffix('Диск (16 мм) усил. под камеру') == '(16 мм) усил. под камеру'


def test_disk_name_suffix_tube_only() -> None:
    assert disk_name_suffix('Диск б/к') == 'б/к'


def test_disk_name_suffix_is_case_insensitive() -> None:
    """Метки распознаются в верхнем регистре."""
    assert disk_name_suffix('Диск (16 мм) УСИЛ. ПОД КАМЕРУ') == '(16 мм) усил. под камеру'


def test_disk_name_suffix_keeps_extras() -> None:
    """Завод и прочие хвосты добавляются к толщине."""
    assert disk_name_suffix('Диск (16 мм) (ABC)') == '(16 мм) (ABC)'


def test_thickness_from_name_comma() -> None:
    """Десятичная запятая в толщине становится точкой."""
    assert thickness_from_name('(15,5 мм)') == '15.5'


def test_thickness_from_name_absent() -> None:
    assert thickness_from_name('без скобок') == ''


def test_fill_disk_thickness_from_title() -> None:
    """Пустая колонка толщины заполняется из хвоста исходного названия."""
    row = RowItem({'title': 'Диск (16 мм)'})

    fill_disk_thickness(row)

    assert row.disk.disk_thickness == '16'


def test_fill_disk_thickness_keeps_existing() -> None:
    """Заполненная колонка не перезаписывается."""
    row = RowItem({'title': 'Диск (16 мм)', 'disk_thickness': '20'})

    fill_disk_thickness(row)

    assert row.disk.disk_thickness == '20'
