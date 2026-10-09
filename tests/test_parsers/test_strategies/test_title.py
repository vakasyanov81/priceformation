"""Стратегии слота `title`: подготовка названия строки."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.normalize import NormalizeTitle
from parsers.strategies.title import (
    DefaultTitle,
    DiskComposeTochki,
    FillFieldsFromTitle,
    ManufacturerFromCategory,
    NormalizeSizeChunks,
    TireCompose,
    TitleWithAliases,
)


def test_default_returns_original_title() -> None:
    assert DefaultTitle().prepare(RowItem({'title': 'Шина'})) == 'Шина'


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('14 iFree Майами лайт 5.5*14 4*98 ET40 D58,5 Хай вэй', '14 iFree Майами лайт 5.5*14 4*98 ET40 D58.5 Хай вэй'),
        ('22 FF 8124 10,0*22 5*130 ET30 D84.1 BMF', '22 FF 8124 10.0*22 5*130 ET30 D84.1 BMF'),
        ('10.00R20 И-281, У-4 TT', '10.00R20 И-281, У-4 TT'),
        ('Nortec   ER-218', 'Nortec ER-218'),
    ],
)
def test_normalize_title_decimal_commas(raw: str, expected: str) -> None:
    """Десятичная запятая становится точкой; запятая не между цифрами не трогается."""
    assert NormalizeTitle().prepare(RowItem({'title': raw})) == expected


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('385/65 R22.5 ...', '385/65R22.5 ...'),
        ('6.00*17.5 , , шт', '6.00x17.5'),
        ('Nortec   ER-218', 'Nortec ER-218'),
        ('31x10,50R15', '31x10.50R15'),
        ('Шина 155/65R13 Armstrong 73T, шт', '155/65R13 Armstrong 73T'),
        ('шина 155/65R13 Armstrong 73T , шт', '155/65R13 Armstrong 73T'),
        ('Шина Nortec', 'Nortec'),
        ('10.00R20 И-281 н.с.8', '10.00R20 И-281 PR8'),
        ('10.00R20 И-281 Н. С. 16', '10.00R20 И-281 PR16'),
        ('а/п 425/85R21 NORTEC TR-184-1 18PR 156J TT, шт', '425/85R21 NORTEC TR-184-1 18PR 156J TT'),
        (
            '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт',
            '10.00R20 DOUBLEROAD DR-801 PR18 149/146K унив.ось с об/л',
        ),
        ('175/70 R13 КАМА ALGA НК-531 шипы НКШЗ автопокрышка, шт', '175/70R13 КАМА ALGA НК-531 шипы НКШЗ'),
        (
            '185/75 R16С Sonix Winter X Pro Studs 77 104/102R шип.автопокрышка, шт',
            '185/75R16С Sonix Winter X Pro Studs 77 104/102R шип.',
        ),
        (
            '11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, (1 шт)',
            '11R22.5 TAITONG HS103 PR16 146/143M вед.ось (1 шт)',
        ),
    ],
)
def test_normalize_size_chunks(raw: str, expected: str) -> None:
    assert NormalizeSizeChunks().prepare(RowItem({'title': raw})) == expected


@pytest.mark.parametrize(
    ('raw', 'has_brand', 'expected'),
    [
        ('Шина 155/65R13 Armstrong 73T', False, 'Алтайшина 155/65R13 Armstrong 73T'),
        ('Шина Nortec', True, 'Nortec'),
        ('Шина', False, 'Алтайшина'),
        ('155/65R13 Armstrong', False, '155/65R13 Armstrong'),
    ],
)
def test_normalize_size_chunks_fallback_brand(raw: str, has_brand: bool, expected: str) -> None:
    """Без бренда ведущая «Шина» → fallback_brand; с брендом — срезается как раньше."""
    strategy = NormalizeSizeChunks('Алтайшина', brand_probe=lambda _title: has_brand)

    assert strategy.prepare(RowItem({'title': raw})) == expected


def test_normalize_size_chunks_without_fallback_strips_ship() -> None:
    """Без fallback_brand поведение прежнее даже при отсутствии бренда."""
    strategy = NormalizeSizeChunks(brand_probe=lambda _title: False)

    assert strategy.prepare(RowItem({'title': 'Шина 155/65R13 Armstrong 73T'})) == '155/65R13 Armstrong 73T'


def test_tire_compose_mim_simple_size() -> None:
    strategy = TireCompose('mim_simple')
    row = RowItem({'width': '205', 'height_percent': '55', 'diameter': '16'})

    assert strategy.prepare(row) == '205/55R16'


def test_tire_compose_mim_simple_non_numeric_profile() -> None:
    strategy = TireCompose('mim_simple')
    row = RowItem({'width': '205', 'height_percent': 'R', 'diameter': '16'})

    assert strategy.prepare(row) == '205/RR16'


def test_tire_compose_mim_truck_size() -> None:
    strategy = TireCompose('mim_truck')
    row = RowItem({'width': '295', 'height_percent': '75', 'diameter': '22.5'})

    assert strategy.prepare(row) == '295/75R22.5'


def test_tire_compose_four_tochki_delegates() -> None:
    strategy = TireCompose('four_tochki')
    row = RowItem({'width': '205', 'diameter': 'R18'})

    assert strategy.prepare(row) == '205R18'


def test_disk_compose_builds_disk_title() -> None:
    strategy = DiskComposeTochki()
    row = RowItem(
        {
            'title': 'Replay HND369',
            'manufacturer_name': 'Replay',
            'model': 'HND369',
            'width': '7.5',
            'diameter': '20',
            'slot_count': '5',
            'pcd1': '114.3',
            'eet': '49.5',
            'central_diameter': '67.1',
            'color': 'MGMF',
        },
    )

    assert strategy.prepare(row) == '7.5x20 5x114.3 ET49.5 67.1 MGMF Replay HND369'


def test_fill_fields_from_title_fills_size() -> None:
    strategy = FillFieldsFromTitle()
    row = RowItem({'title': '205/55R16'})

    assert strategy.prepare(row) == '205/55R16'
    assert row.tire.width == '205'
    assert row.tire.height_percent == '55'
    assert row.tire.diameter == '16'


def test_manufacturer_from_category_prepends_name() -> None:
    strategy = ManufacturerFromCategory(lambda: 'Triangle')
    row = RowItem({'title': 'Nortec ER-218', 'price_opt': 1000})

    strategy.prepare(row)

    assert row.identity.brand == 'Triangle'
    assert row.identity.title == 'Nortec Triangle ER-218'


def test_manufacturer_from_category_maps_alias() -> None:
    strategy = ManufacturerFromCategory(lambda: 'рокбастер')
    row = RowItem({'title': 'Nomex', 'price_opt': 1000})

    strategy.prepare(row)

    assert row.identity.title == 'Nomex RockBuster'


def test_manufacturer_from_category_skips_when_present() -> None:
    strategy = ManufacturerFromCategory(lambda: 'Triangle')
    row = RowItem({'title': 'Triangle Sportex', 'price_opt': 1000})

    strategy.prepare(row)

    assert row.identity.title == 'Triangle Sportex'


def test_manufacturer_from_category_without_price_keeps_title() -> None:
    strategy = ManufacturerFromCategory(lambda: 'Triangle')
    row = RowItem({'title': 'Nortec ER-218'})

    strategy.prepare(row)

    assert row.identity.title == 'Nortec ER-218'


def test_title_with_aliases_replaces() -> None:
    strategy = TitleWithAliases(DefaultTitle(), {'Replay HND': 'Replay Honda'})

    assert strategy.prepare(RowItem({'title': 'Replay HND'})) == 'Replay Honda'


def test_title_with_aliases_keeps_unknown() -> None:
    strategy = TitleWithAliases(DefaultTitle(), {})

    assert strategy.prepare(RowItem({'title': 'Other'})) == 'Other'


def test_title_with_aliases_none_stays_none() -> None:
    strategy = TitleWithAliases(DefaultTitle(), {})

    assert strategy.prepare(RowItem({})) is None
