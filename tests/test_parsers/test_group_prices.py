"""Штатные прайсы размещают только непустые товарные группы."""

import json
from contextlib import closing
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest
from openpyxl import load_workbook

from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.common_price.group_output import output_sources, write_group_prices
from parsers.common_price.tire_output import TireOutputSource
from parsers.writer.output_plan import GroupOutputSource
from parsers.writer.templates.all_templates import writer_templates_by_name
from parsers.writer.templates.group_templates import named_group_output
from tests.group_output_examples import group_writer

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


def test_empty_packages_keep_empty_output_sources(fake_config_provider: FakeConfigProvider) -> None:
    sources = output_sources({}, fake_config_provider)

    paths = write_group_prices(
        group_writer(Path(fake_config_provider.result_folder())),
        sources,
        template=None,
        as_jsonl=False,
        selected={_TIRES, _BATTERIES},
    )

    assert not paths


def test_output_sources_validates_all_known_templates(fake_config_provider: FakeConfigProvider) -> None:
    packages = {_TIRES: TireAndDiskResult()}

    with patch('parsers.common_price.group_output.load_doubles_settings') as load_settings:
        output_sources(packages, fake_config_provider)

    assert load_settings.call_args.args[0] == tuple(writer_templates_by_name())


def test_output_sources_applies_nomenclature_correction(fake_config_provider: FakeConfigProvider) -> None:
    packages = {_TIRES: TireAndDiskResult((RowItem({'title': 'old', 'rest_count': 1}),))}
    output = named_group_output('for_inner')
    settings = next(group for group in output.groups if group.id is _TIRES)

    with patch('parsers.common_price.group_output.get_nomenclature_corrected_title', return_value='fixed') as correct:
        sources = output_sources(packages, fake_config_provider)

    assert sources[_TIRES].prepare('for_inner', settings)[0]['title'] == 'fixed'
    correct.assert_called_once_with('old', config_provider=fake_config_provider)


def test_tire_source_rejects_other_group_with_exact_message(fake_config_provider: FakeConfigProvider) -> None:
    output = named_group_output('for_inner')
    battery_settings = next(group for group in output.groups if group.id is _BATTERIES)
    source = TireOutputSource(TireAndDiskResult())

    with pytest.raises(ValueError, match=r'^Преобразователь tire_and_disk получил настройки другой группы$'):
        source.positions_for('for_inner', battery_settings)


def test_default_outputs_honor_selected_groups(fake_config_provider: FakeConfigProvider) -> None:
    paths = write_group_prices(
        group_writer(Path(fake_config_provider.result_folder())),
        _sources((), fake_config_provider),
        template=None,
        as_jsonl=False,
        selected={_TIRES},
    )

    assert _sheets(paths) == _expected(None, ['Шины и диски'])


def test_named_output_honors_empty_selection(fake_config_provider: FakeConfigProvider) -> None:
    paths = write_group_prices(
        group_writer(Path(fake_config_provider.result_folder())),
        _sources((), fake_config_provider),
        template='for_inner',
        as_jsonl=False,
        selected=set(),
    )

    assert not paths


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
    current_date = date.today().isoformat()
    assert Path(paths[0]).name == f'price_drom_akb_{current_date}.xlsx'
    with closing(load_workbook(paths[0])) as book:
        header, row = list(book['Аккумуляторы'].values)
        assert header == (
            'Тип товара',
            'Бренд',
            'Номенклатура',
            'Цена',
            'Остаток',
            'Наличие',
            'Состояние',
            'Ёмкость, А·ч',
            'Пусковой ток, А',
            'Длина, мм',
            'Ширина, мм',
            'Высота, мм',
            'Тип клемм',
            'Типоразмер',
            'Полярность',
            'Обслуживаемость',
            'Вес',
            'Нижнее крепление',
            'EFB',
            'AGM',
        )
        assert row[0] == 'Аккумулятор'
        assert row[2] == 'АКБ'
        assert row[4] == 1
