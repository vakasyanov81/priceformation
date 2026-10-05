"""Integration test: real four_tochki price parse via entry handlers."""

import logging
from collections.abc import Iterator, Mapping
from pathlib import Path
from unittest.mock import patch

import pytest
from log_watch import LoggerWatcher
from python_calamine import CalamineWorkbook

from cfg import init_cfg
from domain.row_item.row_item import RowField, RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.base_parser_config import make_parse_config
from parsers.vendors.four_tochki.four_tochki_sheet1 import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_params,
)
from parsers.vendors.four_tochki.four_tochki_sheet2 import (
    FourTochkiParser2Sheet,
    fourtochki_sheet_2_params,
)
from run import run_make_price_by_supplier

_INTEGRATION_ROOT = Path(__file__).resolve().parent
_PRICES_DIR = _INTEGRATION_ROOT / 'file_prices_for_test'
_RESULT_DIR = _INTEGRATION_ROOT / 'result_for_test'
_PARSE_CONFIG_DIR = _INTEGRATION_ROOT / 'parse_config_example'
_ROW_LOGGER = 'parsers.base_parser.base_parser_row'


def _four_tochki_vendors() -> list[tuple[type, object]]:
    """fresh ParseConfiguration per run — instance cache stays empty"""
    return [
        (FourTochkiParser1Sheet, make_parse_config(fourtochki_sheet_1_params)),
        (FourTochkiParser2Sheet, make_parse_config(fourtochki_sheet_2_params)),
    ]


def _clear_result_dir() -> None:
    """очищает каталог результатов перед тестом"""
    _RESULT_DIR.mkdir(parents=True, exist_ok=True)
    for path in _RESULT_DIR.glob('*'):
        if path.is_file():
            path.unlink()


@pytest.fixture
def _example_config() -> Iterator[None]:
    init_cfg(
        FakeConfigProvider(
            _INTEGRATION_ROOT,
            config_folder=_PARSE_CONFIG_DIR,
            prices_folder=_PRICES_DIR,
            result_folder=_RESULT_DIR,
        ),
    )
    yield
    init_cfg()


def test_run_make_price_four_tochki_real(_example_config: None) -> None:
    """разбор реального прайса four_tochki и запись результатов в result_for_test."""
    _clear_result_dir()

    with patch('services.parse_orchestrator.all_vendors', return_value=_four_tochki_vendors()):
        run_make_price_by_supplier()

    result_files = sorted(_RESULT_DIR.glob('*.xlsx'))
    assert result_files, 'ожидались xlsx-файлы в result_for_test'
    assert any('price_' in path.name for path in result_files)
    assert any('drom' in path.name for path in result_files)
    assert all(path.stat().st_size > 0 for path in result_files)


# Ожидаемый маппинг колонок four_tochki: индекс, поле позиции, начало заголовка в
# прайсе. Юнит-тесты читают фиктивные строки, поэтому сдвиг колонок они не видят,
# а на реальном прайсе он молча уводит цены и остатки в соседние поля.
type _Layout = tuple[tuple[int, RowField, str], ...]

_TYRE_LAYOUT: _Layout = (
    (0, RowItem.code, 'CAI'),
    (2, RowItem.manufacturer, 'Производитель'),
    (3, RowItem.model, 'Модель'),
    (4, RowItem.width, 'Ширина'),
    (5, RowItem.height_percent, 'Высота'),
    (6, RowItem.diameter, 'Диаметр'),
    (7, RowItem.index_load, 'Индекс нагрузки'),
    (8, RowItem.index_velocity, 'Индекс скорости'),
    (9, RowItem.season, 'Сезон'),
    (10, RowItem.tire_type, 'Тип шины'),
    (11, RowItem.ext_diameter, 'Внешний диаметр'),
    (12, RowItem.spike, 'Шип'),
    (13, RowItem.inscription_on_the_side, 'Надпись на боковине'),
    (14, RowItem.run_flat, 'RunFlat'),
    (15, RowItem.us_aff_designation, 'Американские обозначения'),
    (16, RowItem.camera_type, 'Наличие и тип камеры'),
    (17, RowItem.axis, 'Применяемость по осям'),
    (18, RowItem.layering, 'Норма слойности'),
    (19, RowItem.construction_type, 'Конструкция'),
    (20, RowItem.rest_count, 'Кол-во'),
    (21, RowItem.price_recommended, 'Розница'),
    (22, RowItem.price_opt, 'Цена'),
)
_DISK_LAYOUT: _Layout = (
    (0, RowItem.code, 'CAI'),
    (1, RowItem.title, 'Наименование'),
    (2, RowItem.manufacturer, 'Производитель'),
    (3, RowItem.model, 'Модель'),
    (4, RowItem.color, 'Цвет'),
    (5, RowItem.width, 'Ширина'),
    (6, RowItem.diameter, 'Диаметр'),
    (7, RowItem.slot_count, 'Кол-во отверстий'),
    (8, RowItem.pcd1, 'PCD1'),
    (9, RowItem.pcd2, 'PCD2'),
    (10, RowItem.eet, 'ET'),
    (11, RowItem.central_diameter, 'Dia'),
    (12, RowItem.fastener, 'Крепёж'),
    (13, RowItem.disk_type, 'Тип диска'),
    (14, RowItem.disk_type_1, 'Вид диска'),
    (15, RowItem.main_color, 'Основной цвет'),
    (16, RowItem.disk_thickness, 'Толщина диска'),
    (18, RowItem.rest_count, 'Кол-во'),
    (19, RowItem.price_recommended, 'Розница'),
    (20, RowItem.price_opt, 'Цена'),
)


def _headers(sheet_index: int) -> list[str]:
    """Заголовки прайса: первая строка листа."""
    book = CalamineWorkbook.from_path(_PRICES_DIR / 'four_tochki' / 'price.xlsx')
    rows = book.get_sheet_by_index(sheet_index).to_python(skip_empty_area=False)
    return [str(cell or '') for cell in rows[0]]


def _headers_mismatch(sheet_index: int, layout: _Layout) -> dict[int, tuple[str, str]]:
    """Индексы, где заголовок прайса не похож на ожидаемое поле позиции."""
    headers = _headers(sheet_index)
    mismatch: dict[int, tuple[str, str]] = {}
    for index, _row_field, header in layout:
        if not headers[index].startswith(header):
            mismatch[index] = (headers[index], header)
    return mismatch


@pytest.mark.parametrize(
    ('columns', 'sheet_index', 'layout'),
    [
        (fourtochki_sheet_1_params.columns, 0, _TYRE_LAYOUT),
        (fourtochki_sheet_2_params.columns, 1, _DISK_LAYOUT),
    ],
)
def test_columns_match_price_headers(
    columns: Mapping[int, str],
    sheet_index: int,
    layout: _Layout,
) -> None:
    """каждая спроектированная колонка вендора указывает на своё поле прайса."""
    assert dict(columns) == {index: row_field.name for index, row_field, _header in layout}
    assert not _headers_mismatch(sheet_index, layout)


def test_real_price_rows_have_no_parse_errors(
    _example_config: None,
    watch_logger: LoggerWatcher,
) -> None:
    """реальный прайс разбирается без ошибок строк: сдвинутые колонки их дают тысячи."""
    _clear_result_dir()
    watch = watch_logger(_ROW_LOGGER, logging.ERROR)

    with patch('services.parse_orchestrator.all_vendors', return_value=_four_tochki_vendors()):
        run_make_price_by_supplier()

    errors = [message for _level, message in watch() if 'Не удалось разобрать строку' in message]
    assert not errors
