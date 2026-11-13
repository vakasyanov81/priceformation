"""Маршрутизация исходных строк между секциями одного поставщика."""

import logging
from collections.abc import Sequence
from dataclasses import replace
from typing import Any

import pytest

from domain.exceptions import ConfigValidationError
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.protocols import FileReaderProtocol
from parsers.base_parser.routing import VendorRouting
from parsers.base_parser.routing_rows import RowRoutingError
from parsers.base_parser.section_params import parser_params_from_section
from parsers.raw_table import RawRow, RawTable
from parsers.vendor_config.group_models import TireAndDiskConfig
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.row_selector import RowSelector
from parsers.vendor_config.section_models import VendorSection
from parsers.vendor_config.slot_configs import BehaviorConfig
from parsers.xls_reader import IXlsReader


class _Reader:
    def __init__(self, files: list[str], tables: list[RawTable]) -> None:
        self.files = files
        self.tables = tables
        self.raw_calls: list[str] = []
        self.price_calls: list[Any] = []

    def price_files(self, parser_params: Any) -> list[str]:
        self.price_calls.append(parser_params)
        return self.files

    def raw_tables(self, path: str, sheet_indexes: Sequence[int]) -> list[RawTable]:
        self.raw_calls.append(path)
        selected = set(sheet_indexes)
        selected_tables = []
        for table in self.tables:
            is_json = table.sheet_index is None
            is_selected = not selected or table.sheet_index in selected
            if is_json or is_selected:
                selected_tables.append(table)
        return selected_tables

    def raw_parse(self, path: str, parser_params: Any) -> list[dict[str, Any]]:
        return []

    def get_data_reader(self, path: str, parser_params: Any) -> IXlsReader:
        raise AssertionError('Маршрутизация не использует отображающий читатель')


def _selector(column: str, *accepted: str) -> RowSelector:
    return RowSelector(column, accepted)


def _section(
    identifier: str,
    *,
    selector: RowSelector | None = None,
    start_row: int = 1,
    sheet_indexes: tuple[int, ...] = (),
) -> VendorSection:
    return VendorSection(
        id=identifier,
        name=identifier,
        start_row=start_row,
        file_templates=('*.xlsx',),
        columns={1: 'title'},
        sheet_indexes=sheet_indexes,
        row_selector=selector,
        config_path=f'demo.json → sections[{identifier}]',
    )


def _routing(*sections: VendorSection, reader: str = 'xls') -> VendorRouting:
    config = VendorConfig(
        folder='demo',
        code='demo',
        name='Поставщик',
        reader=reader,
        product_groups=(TireAndDiskConfig(sections, BehaviorConfig()),),
    )
    return VendorRouting(config)


def _row(number: int, fields: dict[str, Any]) -> RawRow:
    return RawRow(fields, number)


def _table(sheet_index: int | None, *rows: RawRow) -> RawTable:
    return RawTable(sheet_index, rows)


def test_shared_sheet_routes_before_mapping_and_counts_unrouted(caplog: pytest.LogCaptureFixture) -> None:
    routing = _routing(
        _section('tires', selector=_selector('0', 'шина'), start_row=2),
        _section('disks', selector=_selector('0', 'диск'), start_row=2),
    )
    table = _table(
        0,
        _row(1, {'0': 'тип', '1': 'заголовок'}),
        _row(2, {'0': 'шина', '1': ' Шина А '}),
        _row(3, {'0': 'диск', '1': ' Диск Б '}),
        _row(4, {'0': 'другое', '1': 'Пропуск'}),
        _row(5, {'0': ' шина', '1': 'Без strip'}),
        _row(6, {'0': 7, '1': 'Не строка'}),
        _row(7, {'0': None, '1': None}),
    )
    reader = _Reader(['prices.xlsx'], [table])

    assert routing.resolve('tires', reader) == ['prices.xlsx']
    assert routing.resolve('disks', reader) == ['prices.xlsx']
    assert routing.read_rows('tires') == [{'title': 'Шина А'}]
    assert routing.read_rows('disks') == [{'title': 'Диск Б'}]
    assert routing.unrouted_rows == 3
    assert reader.raw_calls == ['prices.xlsx']
    assert [call.supplier.code for call in reader.price_calls] == ['tires', 'disks']
    assert [(call.start_row, call.file_templates, call.sheet_indexes) for call in reader.price_calls] == [
        (2, ('*.xlsx',), ()),
        (2, ('*.xlsx',), ()),
    ]
    assert 'Поставщик: файл prices.xlsx, лист 1: пропущено строк — 3' in caplog.text
    assert 'не подходят под настройки отбора разделов или товаров' in caplog.text
    assert caplog.records[0].levelno == logging.WARNING


def test_same_file_and_template_do_not_duplicate_section_reading() -> None:
    tires = _section('tires', sheet_indexes=(0,))
    other = _section('other', sheet_indexes=(1,))
    routing = _routing(tires, other)
    tables = [
        _table(0, _row(1, {'1': 'Шина'})),
        _table(1, _row(1, {'1': 'Диск'})),
    ]
    reader = _Reader(['prices.xlsx', 'prices.xlsx'], tables)

    assert routing.resolve('tires', reader) == ['prices.xlsx']
    assert routing.read_rows('tires') == [{'title': 'Шина'}]
    assert routing.read_rows('other') == [{'title': 'Диск'}]
    assert reader.raw_calls == ['prices.xlsx']


def test_unselected_sheet_is_not_routed() -> None:
    routing = _routing(_section('tires', sheet_indexes=(0,)))
    tables = [
        _table(0, _row(1, {'1': 'Шина'})),
        _table(1, _row(1, {'1': 'Чужой лист'})),
    ]
    reader = _Reader(['prices.xlsx'], tables)

    routing.resolve('tires', reader)

    assert routing.read_rows('tires') == [{'title': 'Шина'}]
    assert routing.unrouted_rows == 0


def test_shared_sheet_requires_selectors_before_rows() -> None:
    tires = _section('tires')
    disks = _section('disks', selector=_selector('0', 'диск'))
    routing = _routing(tires, disks)
    row = _row(1, {'0': 'диск'})
    reader = _Reader(['prices.xlsx'], [_table(0, row)])
    routing.resolve('tires', reader)

    with pytest.raises(ConfigValidationError, match='каждая секция должна задать row_selector'):
        routing.read_rows('tires')


def test_shared_sheet_requires_common_start_row_with_both_paths() -> None:
    tires = _section('tires', selector=_selector('0', 'шина'))
    disks = _section('disks', selector=_selector('0', 'диск'), start_row=2)
    routing = _routing(tires, disks)
    reader = _Reader(['prices.xlsx'], [_table(0)])
    routing.resolve('tires', reader)

    with pytest.raises(ConfigValidationError) as error:
        routing.read_rows('tires')

    assert 'sections[tires] → start_row' in str(error.value)
    assert 'sections[disks] → start_row' in str(error.value)


def test_statically_overlapping_selectors_are_rejected() -> None:
    tires = _section('tires', selector=_selector('0', 'шина', 'общее'))
    disks = _section('disks', selector=_selector('0', 'диск', 'общее'))
    routing = _routing(tires, disks)
    reader = _Reader(['prices.xlsx'], [_table(0)])
    routing.resolve('tires', reader)

    with pytest.raises(ConfigValidationError, match='пересекаются'):
        routing.read_rows('tires')


def test_dynamic_overlap_reports_row_and_all_routes() -> None:
    tires = _section('tires', selector=_selector('0', 'товар'))
    disks = _section('disks', selector=_selector('1', 'да'))
    routing = _routing(tires, disks)
    row = _row(4, {'0': 'товар', '1': 'да'})
    reader = _Reader(['prices.xlsx'], [_table(0, row)])
    routing.resolve('tires', reader)

    with pytest.raises(RowRoutingError) as error:
        routing.read_rows('tires')

    assert str(error.value) == (
        'Поставщик demo, файл prices.xlsx, лист 0, строка 4: '
        'неоднозначная маршрутизация — tires (tire_and_disk), disks (tire_and_disk)'
    )


def test_json_unrouted_log_identifies_json_source(caplog: pytest.LogCaptureFixture) -> None:
    routing = _routing(_section('tires', selector=_selector('kind', 'шина')), reader='json')
    table = _table(None, _row(1, {'kind': 'другое'}))
    reader = _Reader(['prices.json'], [table])
    routing.resolve('tires', reader)

    assert routing.read_rows('tires') == []
    assert routing.unrouted_rows == 1
    assert 'Поставщик: файл prices.json, лист JSON: пропущено строк — 1' in caplog.text


def test_missing_selected_sheet_is_an_error() -> None:
    routing = _routing(_section('tires', sheet_indexes=(2,)))
    reader: FileReaderProtocol = _Reader(['prices.xlsx'], [_table(0)])
    routing.resolve('tires', reader)

    with pytest.raises(ConfigValidationError, match=r'листы \[2\] отсутствуют'):
        routing.read_rows('tires')


def test_price_files_pass_explicit_paths_to_shared_routing() -> None:
    section = _section('tires')
    routing = _routing(section)
    table = _table(0, _row(1, {'1': 'Шина'}))
    reader = _Reader(['discovered.xlsx'], [table])
    price_files = PriceFiles(parser_params_from_section(section, 'demo'), reader, routing)
    price_files.files = ['given.xlsx']

    assert price_files.resolve() == ['given.xlsx']
    positions = price_files.read_positions(price_files.files or [], lambda row: row)
    assert positions == [{'title': 'Шина'}]
    assert reader.raw_calls == ['given.xlsx']


def test_json_routing_preserves_values_and_ignores_missing_columns() -> None:
    section = replace(
        _section('tires', selector=_selector('kind', 'шина')),
        columns={'source': 'title', 'missing': 'model'},
    )
    routing = _routing(section, reader='json')
    row = _row(1, {'kind': 'шина', 'source': ' Шина без strip '})
    reader = _Reader(['prices.json'], [_table(None, row)])
    routing.resolve('tires', reader)

    assert routing.read_rows('tires') == [{'title': ' Шина без strip '}]
