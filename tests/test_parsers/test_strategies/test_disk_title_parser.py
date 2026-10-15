"""Разбор названия диска Пошка и STK."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies._disk_title_parser import DiskTitleParts, fill_disk_fields, parse_disk_title


def _parsed(raw: str) -> DiskTitleParts:
    parts = parse_disk_title(raw)
    assert parts is not None
    return parts


@pytest.mark.parametrize(
    ('raw', 'width', 'diameter', 'slots', 'pcd'),
    [
        ('Диск штамп SRW 11.75x22.5 10x335 ET135 d281 М22 Silver (13мм) 4500 кг', '11.75', '22.5', '10', '335'),
        ('Диск штамп BTRW 5.5x16 6x170 ET106 d130 усил. 1250 кг', '5.5', '16', '6', '170'),
        ('Диск штамп Kronprinz 6x15 5x139.7 ЕТ22 d108.5 УАЗ 450 грунт (4.5 мм) 750 кг', '6', '15', '5', '139.7'),
        ('Диск штамп ZEPP B19DS44.4 6.00x17.5 6x222.25 ET135 d164 Sil (10мм)', '6.00', '17.5', '6', '222.25'),
        ('Диск штамп Forza F-14 9x22.5 10 отв. ET175 d222', '9', '22.5', '10', ''),
        ('Диск стальной Yongzheng 22.5x11.75 10 26мм ЕТ0 D281 раст.335 (16мм)', '11.75', '22.5', '10', '335'),
        ('Диск стальной Yongzheng 22.5x9.00 10 26мм ЕТ175 D281 раст.335 (18мм)', '9.00', '22.5', '10', '335'),
        ('Диск штамп 5x10 (две половинки)', '5', '10', '', ''),
        ('Диск штамп Тольятти 5,5х16 5х139,7 ET52 d98', '5.5', '16', '5', '139.7'),
    ],
)
def test_parse_size_and_fasteners(raw: str, width: str, diameter: str, slots: str, pcd: str) -> None:
    """Размер (порядок «диаметр x ширина» у STK тоже) и крепёж из каждого формата."""
    parts = _parsed(raw)

    assert (parts.width, parts.diameter) == (width, diameter)
    assert (parts.slot_count, parts.pcd) == (slots, pcd)


@pytest.mark.parametrize(
    ('raw', 'et', 'central'),
    [
        ('Диск штамп Nortec-16 11.75x22.5 10x335 ET0 d281', '0', '281'),
        ('Диск штамп Kronprinz 6x15 5x139.7 ЕТ22 d108.5 грунт', '22', '108.5'),
        ('Диск стальной Yongzheng 22.5x9.00 10 26мм ЕТ175 D281 раст.335', '175', '281'),
        ('Диск штамп 5x10 (две половинки)', '', ''),
    ],
)
def test_parse_et_and_central_diameter(raw: str, et: str, central: str) -> None:
    """ET (латиницей и кириллической Е) и DIA (d/D)."""
    parts = _parsed(raw)

    assert (parts.et, parts.central_diameter) == (et, central)


@pytest.mark.parametrize(
    ('raw', 'thickness'),
    [
        ('Диск штамп SRW 11.75x22.5 10x335 ET135 d281 М22 Silver (13мм) 4500 кг', '13'),
        ('Диск штамп SRW 5.5x16 6x170 ET106 d130 Газель серебристый (8 мм) 1 350 кг', '8'),
        ('Диск штамп Next 11.75x22.5 10x335 ET120 d281 16мм', '16'),
        ('Диск стальной Yongzheng 22.5x11.75 10 26мм ЕТ0 D281 раст.335', ''),
        ('Диск штамп Nortec 5.5x16 6x170 ET106 d130 усил. 1250 кг', ''),
    ],
)
def test_parse_thickness_ignores_hole_diameter(raw: str, thickness: str) -> None:
    """Толщина в скобках или голая; ``26мм`` после числа отверстий — диаметр отверстия, не толщина."""
    assert _parsed(raw).thickness == thickness


@pytest.mark.parametrize(
    ('raw', 'color'),
    [
        ('Диск штамп SRW 5.5x16 6x170 ET106 d130 усил. 1500 кг Silver', 'Silver'),
        ('Диск штамп ZEPP 6.75x17.5 10x225 ET135 d176 M22 (12 мм) Sil', 'Silver'),
        ('Диск штамп SRW 5.5x16 6x170 ET106 d130 Газель серебристый (8 мм)', 'серебристый'),
        ('Диск штамп Тольятти 5.5x16 5x139.7 ET52 d98 НИВА (серебристый) ТЗСК', 'серебристый'),
        ('Диск штамп ТЗСК 6.5x16 5x139.7 ET40 d108 УАЗ-Патриот металлик', 'металлик'),
        ('Диск штамп Kronprinz 6x15 5x139.7 ЕТ22 d108.5 УАЗ 450 грунт', 'грунт'),
        ('Диск штамп Nortec-16 11.75x22.5 10x335 ET0 d281', ''),
    ],
)
def test_parse_color(raw: str, color: str) -> None:
    assert _parsed(raw).color == color


@pytest.mark.parametrize(
    ('raw', 'disk_type'),
    [
        ('Диск штамп Nortec-16 11.75x22.5 10x335 ET0 d281', 'штамп'),
        ('Диск стальной Yongzheng 22.5x9.00 10 26мм ЕТ175 D281 раст.335', 'стальной'),
        ('Диск Nortec-16 11.75x22.5 10x335 ET0 d281', ''),
    ],
)
def test_parse_disk_type(raw: str, disk_type: str) -> None:
    assert _parsed(raw).disk_type == disk_type


@pytest.mark.parametrize(
    'raw',
    [None, '', 'Шина 215/75R17.5 Triangle TR685', 'Диск штамп без размера', 'Диск штамп Nortec 10x335'],
    ids=['none', 'empty', 'tire', 'no-size', 'only-fasteners'],
)
def test_parse_returns_none_for_non_disk(raw: str | None) -> None:
    assert parse_disk_title(raw) is None


def test_fill_disk_fields_sets_row_fields() -> None:
    raw = 'Диск штамп SRW 11.75x22.5 10x335 ET135 d281 М22 Silver (13мм) 4500 кг'
    row = RowItem({'title': raw})

    fill_disk_fields(row, _parsed(raw))

    assert (row.tire.width, row.tire.diameter) == ('11.75', '22.5')
    assert (row.disk.slot_count, row.disk.pcd1) == (10, 335)
    assert (row.disk.eet, row.disk.central_diameter) == (135, 281)
    assert (row.disk.disk_thickness, row.disk.color) == ('13', 'Silver')
    assert row.disk.disk_type == 'штамп'


def test_fill_disk_fields_keeps_existing_values() -> None:
    raw = 'Диск штамп SRW 5.5x16 6x170 ET106 d130 Silver'
    row = RowItem({'title': raw, 'color': 'Чёрный'})

    fill_disk_fields(row, _parsed(raw))

    assert row.disk.color == 'Чёрный'


def test_fill_disk_fields_title_overrides_eet_column() -> None:
    """Вылет из названия главнее колонки: у колонки Запаски одно значение на модель."""
    raw = 'Диск штамп SRW 5.5x16 6x170 ET106 d130 Silver'
    row = RowItem({'title': raw, 'eet': 40})

    fill_disk_fields(row, _parsed(raw))

    assert row.disk.eet == 106


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('15 Khomen KHW1501 ZV Vesta/Almera 6.0*15 4*100 ET50 D60.1 GRAY', '50'),
        ('16 Trebl 5.5*16 6*170 ЕТ105 130.1 S 1000 кг. паллета', '105'),
        ('6.0x15 4x100 ET-10 60.1 Black', '-10'),
        ('14 TREBL 5.5*14 4*108 ET37.5 63.3 S', '37.5'),
        ('5.5x16 6x180 ET109.5 138.8 Серебро Тзск Ford Transit', '109.5'),
        ('33x10.50-16 Nortec ET-500 111N TL', None),
        ('15 Khomen KHW1501 6.0*15 GRAY', None),
        (None, None),
    ],
)
def test_et_from_name_needs_fasteners(raw: str | None, expected: str | None) -> None:
    """ET берём только из названия с крепежом `4*100`: `ET-500` у шины — не вылет."""
    assert DiskTitleParts.et_from_name(raw) == expected
