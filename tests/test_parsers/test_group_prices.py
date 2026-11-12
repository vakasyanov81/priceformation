"""Штатные прайсы размещают только непустые товарные группы."""

import json
from contextlib import closing
from pathlib import Path

import pytest
from openpyxl import load_workbook

from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from integration_tests.group_xlsx_examples import group_writer
from parsers.common_price.group_output import output_sources, write_group_prices
from parsers.writer.output_plan import GroupOutputSource

_TIRES = ProductGroup.TIRE_AND_DISK
_BATTERIES = ProductGroup.BATTERIES


def _sources(empty: tuple[ProductGroup, ...], config: FakeConfigProvider) -> dict[ProductGroup, GroupOutputSource]:
    tires: tuple[RowItem, ...] = (RowItem({'title': 'Шина', 'rest_count': 1}),)
    if _TIRES in empty:
        tires = ()
    batteries: tuple[BatteryItem, ...] = (BatteryItem.from_fields({'title': 'АКБ', 'rest_count': 1}),)
    if _BATTERIES in empty:
        batteries = ()
    return output_sources({_TIRES: TireAndDiskResult(tires), _BATTERIES: BatteryResult(batteries)}, config)


def _expected(template: str | None, names: list[str]) -> list[list[str]]:
    books = [names] if names and template != 'for_drom' else []
    if template != 'for_inner':
        books.extend([['price' if name == 'Шины и диски' else name] for name in names])
    return books


def _sheets(paths: list[str]) -> list[list[str]]:
    books = []
    for path in paths:
        with closing(load_workbook(path)) as book:
            books.append(book.sheetnames)
            assert all(sheet.max_row > 1 for sheet in book)
    return books


@pytest.mark.parametrize('template', [None, 'for_inner', 'for_drom'])
@pytest.mark.parametrize(
    'empty, names',
    [
        ((), ['Шины и диски', 'Аккумуляторы']),
        ((_TIRES,), ['Аккумуляторы']),
        ((_BATTERIES,), ['Шины и диски']),
        ((_TIRES, _BATTERIES), []),
    ],
)
def test_group_prices_skip_empty_groups(
    fake_config_provider: FakeConfigProvider,
    template: str | None,
    empty: tuple[ProductGroup, ...],
    names: list[str],
) -> None:
    folder = Path(fake_config_provider.result_folder())
    paths = write_group_prices(
        group_writer(folder),
        _sources(empty, fake_config_provider),
        template=template,
        as_jsonl=False,
        selected={_TIRES, _BATTERIES},
    )
    assert _sheets(paths) == _expected(template, names)
    written = [str(path) for path in folder.iterdir()]
    assert sorted(written) == sorted(paths)


def test_jsonl_skips_empty_group_metadata(fake_config_provider: FakeConfigProvider) -> None:
    folder = Path(fake_config_provider.result_folder())
    paths = write_group_prices(
        group_writer(folder),
        _sources((_TIRES,), fake_config_provider),
        template=None,
        as_jsonl=True,
        selected={_TIRES, _BATTERIES},
    )
    metadata = json.loads((folder / 'result_meta.json').read_text())
    groups = {schema['product_group'] for schema in metadata['files'].values()}
    assert groups == {_BATTERIES.value}
    assert len(metadata['files']) == 2
    assert len(paths) == 3


def test_drom_battery_columns(fake_config_provider: FakeConfigProvider) -> None:
    paths = write_group_prices(
        group_writer(Path(fake_config_provider.result_folder())),
        _sources((_TIRES,), fake_config_provider),
        template='for_drom',
        as_jsonl=False,
        selected={_TIRES, _BATTERIES},
    )
    with closing(load_workbook(paths[0])) as book:
        header, row = list(book['Аккумуляторы'].values)
        assert header == ('Тип товара', 'Бренд', 'Номенклатура', 'Цена', 'Остаток', 'Наличие', 'Состояние')
        assert row[0] == 'Аккумулятор'
        assert row[2] == 'АКБ'
        assert row[4] == 1
