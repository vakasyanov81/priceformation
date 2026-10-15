"""Обёртка `params_from_title`: параметры шин и дисков из названия в поля позиции."""

from domain.row_item.row_item import RowItem
from parsers.strategies.poshk_stk_title import PoshkStkTireCompose
from parsers.strategies.title import DefaultTitle, ManufacturerFromCategory
from parsers.strategies.title_params import ParamsFromTitle

_PIONER = '215/75R17.5 Triangle TR685 135/133L 16PR TL рулевая'


def test_fills_disk_fields_and_keeps_title() -> None:
    raw = 'Диск штамп Nortec-16 11.75x22.5 10x335 ET0 d281'
    row = RowItem({'title': raw})

    assert ParamsFromTitle(DefaultTitle()).prepare(row) == raw
    assert row.disk.pcd1 == 335
    assert row.disk.eet == 0


def test_fills_tire_fields_for_pioner() -> None:
    row = RowItem({'title': _PIONER, 'price_opt': 1000})

    strategy = ParamsFromTitle(ManufacturerFromCategory(lambda: 'Triangle'))

    assert strategy.prepare(row) == _PIONER
    assert (row.tire.width, row.tire.height_percent) == ('215', '75')
    assert row.tire.diameter == '17.5'
    assert (row.tire.index_load, row.tire.index_velocity) == ('135/133', 'L')
    assert (row.tire.layering, row.tire.intimacy) == ('16PR', 'TL')
    assert row.identity.model == 'TR685'


def test_parses_title_after_manufacturer_is_prepended() -> None:
    """Производитель раздела вставлен в название до разбора: модель не принимает его за бренд."""
    row = RowItem({'title': '215/75R17.5 TR685 135/133L', 'price_opt': 1000})

    ParamsFromTitle(ManufacturerFromCategory(lambda: 'Triangle')).prepare(row)

    assert row.identity.model == 'TR685'


def test_fills_tire_fields_from_poshk_compose() -> None:
    row = RowItem({'title': 'Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал'})

    ParamsFromTitle(PoshkStkTireCompose('', None)).prepare(row)

    assert (row.tire.width, row.tire.height_percent) == ('235', '75')
    assert row.identity.model == 'LLA78'


def test_fills_without_price() -> None:
    row = RowItem({'title': _PIONER})

    ParamsFromTitle(ManufacturerFromCategory(lambda: 'Triangle')).prepare(row)

    assert row.tire.width == '215'


def test_keeps_existing_values() -> None:
    row = RowItem({'title': _PIONER, 'width': '999'})

    ParamsFromTitle(DefaultTitle()).prepare(row)

    assert row.tire.width == '999'


def test_ignores_unparsable_title() -> None:
    row = RowItem({'title': 'Камера 12.5/80-18'})

    assert ParamsFromTitle(DefaultTitle()).prepare(row) == 'Камера 12.5/80-18'
    assert row.tire.width is None


def test_keeps_none_title() -> None:
    assert ParamsFromTitle(DefaultTitle()).prepare(RowItem({})) is None
