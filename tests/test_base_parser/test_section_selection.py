"""Выбор товаров по корневому разделу до преобразования входных ячеек."""

import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from openpyxl import Workbook

from domain.exceptions import ConfigValidationError
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.routing import VendorRouting
from parsers.base_parser.routing_rows import RowRoutingError
from parsers.base_parser.section_selection import SectionSelection
from parsers.raw_table import RawRow
from parsers.vendor_config.group_models import BatteryConfig
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.section_selector import SectionSelector


def _config() -> VendorConfig:
    path = Path('tests/parse_config_example/plant.json')
    return VendorConfig.from_dict(json.loads(path.read_text()), 'plant', str(path))


def _price(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    for title, stock in (
        ('Название', 'Остаток'),
        ('АКБ Авто 10.11.2026', None),
        ('    Производитель', None),
        ('       Масла (вложенный раздел)', None),
        ('            XTREME +EFB 60', 2),
        ('Масла', None),
        ('    АКБ (вложенный раздел)', None),
        ('            XTREME +EFB масло', 3),
        ('Фильтры', None),
        ('            АКБ фильтр', 4),
        ('акб Мото', None),
        ('            XTREME Arctic 60', 5),
    ):
        sheet.append([None, title, stock, 5000 if stock else None])
    other = workbook.create_sheet('Без заголовка')
    other.append([None, '            Чужой товар', 1, 5000])
    workbook.save(path)
    workbook.close()


def _routes(path: Path, *keywords: str) -> VendorRouting:
    config = _config()
    battery_group = config.product_groups[0]
    assert isinstance(battery_group, BatteryConfig)
    first = battery_group.sections[0]
    sections = tuple(
        replace(
            first,
            id=keyword,
            start_row=5,
            columns={1: 'title', 2: 'rest_count'},
            sheet_indexes=(),
            section_selector=SectionSelector('1', (keyword.casefold(),)),
        )
        for keyword in keywords
    )
    group = replace(battery_group, sections=sections)
    config = replace(config, product_groups=(group,))
    routing = VendorRouting(config)
    reader = FileReader(price_source=MagicMock())
    routing.resolve(sections[0].id, reader, [str(path)])
    return routing


def test_xlsx_routes_by_root_before_start_row_and_resets_on_next_sheet(tmp_path: Path) -> None:
    path = tmp_path / 'plant.xlsx'
    _price(path)
    routing = _routes(path, 'АКБ', 'Масла')
    assert routing.read_rows('АКБ') == [
        {'title': 'XTREME +EFB 60', 'rest_count': 2},
        {'title': 'XTREME Arctic 60', 'rest_count': 5},
    ]
    assert routing.read_rows('Масла') == [{'title': 'XTREME +EFB масло', 'rest_count': 3}]


def test_overlapping_root_keywords_report_ambiguous_product(tmp_path: Path) -> None:
    path = tmp_path / 'plant.xlsx'
    _price(path)
    routing = _routes(path, 'АКБ', 'Авто')
    with pytest.raises(RowRoutingError, match='строка 5'):
        routing.read_rows('АКБ')


@pytest.mark.parametrize(
    'raw',
    [
        None,
        [],
        {},
        {'column': '1', 'keywords': []},
        {'column': '1', 'keywords': [' ']},
        {'column': '1', 'keywords': [1]},
        {'column': 1, 'keywords': ['АКБ']},
    ],
)
def test_invalid_section_selector_reports_config_path(raw: object) -> None:
    with pytest.raises(ConfigValidationError, match=r'plant\.json → section_selector'):
        SectionSelector.from_payload({'section_selector': raw}, 'plant.json')


def test_selector_normalizes_keywords_and_accepts_any_match() -> None:
    selector = SectionSelector.from_payload(
        {'section_selector': {'column': '1', 'keywords': [' АКБ ', 'Батареи']}}, 'plant.json'
    )
    assert selector is not None
    assert selector.matches('акб Авто')
    assert selector.matches('БАТАРЕИ мото')
    assert not selector.matches('Масла')


@pytest.mark.parametrize('title', [None, 12, '', '   '])
def test_selection_ignores_missing_and_nontext_titles(title: object) -> None:
    selection = SectionSelection(SectionSelector('1', ('акб',)))
    assert not selection.accepts(RawRow({'1': title, '2': 1}, 1))


def test_selection_rejects_products_before_root_and_preserves_zero_stock() -> None:
    selection = SectionSelection(SectionSelector('1', ('акб',)))
    product = RawRow({'1': '    Товар', '2': 0}, 1)
    assert not selection.accepts(product)
    assert not selection.accepts(RawRow({'1': 'АКБ', '2': ''}, 2))
    assert selection.accepts(product)


def test_plant_group_filter_is_inherited_by_sections() -> None:
    section = _config().product_groups[0].sections[0]
    assert section.section_selector == SectionSelector('1', ('акб',))
