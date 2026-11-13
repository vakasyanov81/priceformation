"""Отчёт дублей сохраняет модели товарных групп на отдельных листах."""

from contextlib import closing
from dataclasses import replace
from pathlib import Path

import pytest
from openpyxl import load_workbook

from domain.battery.duplicate import BatteryDuplicate
from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.common_price.group_output import output_sources, write_group_prices
from tests.group_output_examples import group_writer

_TIRES = ProductGroup.TIRE_AND_DISK
_BATTERIES = ProductGroup.BATTERIES


def _batteries() -> BatteryResult:
    position = BatteryItem.from_fields({'title': 'АКБ', 'price_recommended': '5000', 'rest_count': 1})
    return BatteryResult(
        tuple(
            replace(position, duplicate=mark)
            for mark in (
                BatteryDuplicate(1, True),
                BatteryDuplicate(1, False),
                BatteryDuplicate(2, True),
                BatteryDuplicate(),
            )
        )
    )


@pytest.mark.parametrize(
    'empty, names',
    [
        ((), ['Шины и диски', 'Аккумуляторы']),
        ((_TIRES,), ['Аккумуляторы']),
        ((_BATTERIES,), ['Шины и диски']),
        ((_TIRES, _BATTERIES), []),
    ],
)
def test_default_doubles_sheets(
    fake_config_provider: FakeConfigProvider,
    empty: tuple[ProductGroup, ...],
    names: list[str],
) -> None:
    packages = duplicate_packages(empty)
    paths = write_group_prices(
        group_writer(Path(fake_config_provider.result_folder())),
        output_sources(packages, fake_config_provider),
        template=None,
        as_jsonl=False,
        selected=packages.keys(),
    )
    reports = [path for path in paths if Path(path).name.startswith('doubles_')]
    assert len(reports) == bool(names)
    for path in reports:
        with closing(load_workbook(path)) as book:
            assert book.sheetnames == names
            if _BATTERIES not in empty:
                assert book['Аккумуляторы'].max_row == 3


def duplicate_packages(empty: tuple[ProductGroup, ...]) -> dict[ProductGroup, TireAndDiskResult | BatteryResult]:
    return {
        _TIRES: TireAndDiskResult((RowItem({'title': 'Шина', 'is_double': _TIRES not in empty}),)),
        _BATTERIES: BatteryResult() if _BATTERIES in empty else _batteries(),
    }
