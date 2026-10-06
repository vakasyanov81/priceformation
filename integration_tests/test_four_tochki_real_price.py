"""Integration test: real four_tochki price parse via config-driven parser."""

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from log_watch import LoggerWatcher
from python_calamine import CalamineWorkbook

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.registry import vendor_entry_for
from parsers.vendor_config.provider import load_vendor_configs
from services.parse_orchestrator import ParseOrchestrator

_INTEGRATION_ROOT = Path(__file__).resolve().parent
_PRICES_DIR = _INTEGRATION_ROOT / 'file_prices_for_test'
_PROJECT_ROOT = _INTEGRATION_ROOT.parent
_ROW_LOGGER = 'parsers.base_parser.base_parser_row'


def _four_tochki_file() -> str:
    return str(_PRICES_DIR / 'four_tochki' / 'price.xlsx')


@pytest.fixture
def _four_tochki_provider() -> Iterator[None]:
    """Провайдер путей: parse_config — из проекта (vendors/*.json), цены — из фикстур."""
    init_cfg(
        FakeConfigProvider(
            _INTEGRATION_ROOT,
            config_folder=_PROJECT_ROOT / 'parse_config',
            prices_folder=_PRICES_DIR,
            result_folder=_INTEGRATION_ROOT / 'result_for_test',
        ),
    )
    yield
    init_cfg()


# Ожидаемый маппинг колонок four_tochki: (индекс, имя_поля_в_конфиге, начало_заголовка_в_прайсе).
type _Layout = tuple[tuple[int, str, str], ...]

_TYRE_LAYOUT: _Layout = (
    (0, 'code', 'CAI'),
    (2, 'manufacturer', 'Производитель'),
    (3, 'model', 'Модель'),
    (4, 'width', 'Ширина'),
    (5, 'height_percent', 'Высота'),
    (6, 'diameter', 'Диаметр'),
    (7, 'index_load', 'Индекс нагрузки'),
    (8, 'index_velocity', 'Индекс скорости'),
    (9, 'season', 'Сезон'),
    (10, 'tire_type', 'Тип шины'),
    (11, 'ext_diameter', 'Внешний диаметр'),
    (12, 'spike', 'Шип'),
    (13, 'inscription_on_the_side', 'Надпись на боковине'),
    (14, 'run_flat', 'RunFlat'),
    (15, 'us_aff_designation', 'Американские обозначения'),
    (16, 'camera_type', 'Наличие и тип камеры'),
    (17, 'axis', 'Применяемость по осям'),
    (18, 'layering', 'Норма слойности'),
    (19, 'construction_type', 'Конструкция'),
    (20, 'rest_count', 'Кол-во'),
    (21, 'price_recommended', 'Розница'),
    (22, 'price_opt', 'Цена'),
)
_DISK_LAYOUT: _Layout = (
    (0, 'code', 'CAI'),
    (1, 'title', 'Наименование'),
    (2, 'manufacturer', 'Производитель'),
    (3, 'model', 'Модель'),
    (4, 'color', 'Цвет'),
    (5, 'width', 'Ширина'),
    (6, 'diameter', 'Диаметр'),
    (7, 'slot_count', 'Кол-во отверстий'),
    (8, 'pcd1', 'PCD1'),
    (9, 'pcd2', 'PCD2'),
    (10, 'eet', 'ET'),
    (11, 'central_diameter', 'Dia'),
    (12, 'fastener', 'Крепёж'),
    (13, 'disk_type', 'Тип диска'),
    (14, 'disk_type_1', 'Вид диска'),
    (15, 'main_color', 'Основной цвет'),
    (16, 'disk_thickness', 'Толщина диска'),
    (18, 'rest_count', 'Кол-во'),
    (19, 'price_recommended', 'Розница'),
    (20, 'price_opt', 'Цена'),
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
    for index, _field_name, header in layout:
        if not headers[index].startswith(header):
            mismatch[index] = (headers[index], header)
    return mismatch


@pytest.mark.parametrize(
    ('section_index', 'sheet_index', 'layout'),
    [
        (0, 0, _TYRE_LAYOUT),
        (1, 1, _DISK_LAYOUT),
    ],
)
def test_columns_match_price_headers(
    section_index: int,
    sheet_index: int,
    layout: _Layout,
) -> None:
    """каждая спроектированная колонка вендора указывает на своё поле прайса."""
    cfg = load_vendor_configs()['four_tochki']
    section = cfg.sections[section_index]
    columns = section.columns
    assert dict(columns) == {index: field_name for index, field_name, _header in layout}
    assert not _headers_mismatch(sheet_index, layout)


def test_real_price_rows_have_no_parse_errors(
    _four_tochki_provider: None,
    watch_logger: LoggerWatcher,
) -> None:
    """реальный прайс разбирается без ошибок строк."""
    watch = watch_logger(_ROW_LOGGER, logging.ERROR)
    orchestrator = ParseOrchestrator()
    orchestrator.parse_all([vendor_entry_for('5')])
    errors = [message for _level, message in watch() if 'Не удалось разобрать строку' in message]
    assert not errors, f'Обнаружены ошибки разбора: {errors}'
