"""
tests write duplicates report
"""

import datetime
from typing import Any

from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.xls_writer import XlsWriter
from tests.fakes.fake_driver import FakeXlwtDriver

from .fixtures import result_body_inner, write_data

_GROUP_COL = 0
_IS_DOUBLE_COL = 20
_DISPUTED_COL = 21
_COLUMNS_IN_ROW = len(result_body_inner) + 2
_LEGEND = [
    ('#ccffcc', 'Главный дубль группы'),
    ('#ff9999', 'Сомнительный дубль: цена отклоняется от главного на 5% и более'),
]
_FIRST_ROW = len(_LEGEND) + 2
_ROW_SHIFT = _FIRST_ROW - 1


def _coords(key: str) -> tuple[int, int]:
    row, col = key.removeprefix('cell(').removesuffix(')').split(',')
    return int(row), int(col)


def _shift(key: str) -> str:
    """ключ ячейки внутреннего прайса: на колонку правее («Группа по параметрам») и ниже легенды"""
    row, col = _coords(key)
    shifted = (row + _ROW_SHIFT, col + 1)
    return f'cell({shifted[0]},{shifted[1]})'


def _write(rows: list[dict[str, Any]], tmp_path: Any) -> FakeXlwtDriver:
    fake_driver = FakeXlwtDriver()
    XlsWriter(fake_driver, rows, template=ForDoubles, result_folder=str(tmp_path)).write()
    return fake_driver


def _data_cells(fake_driver: FakeXlwtDriver) -> dict[str, Any]:
    """ячейки данных (без легенды)"""
    return {key: cell for key, cell in fake_driver.body.items() if _in_data(key)}


def _in_data(key: str) -> bool:
    return int(key.removeprefix('cell(').split(',')[0]) >= _FIRST_ROW


def _data_colors(fake_driver: FakeXlwtDriver) -> dict[str, str]:
    """цвета ячеек данных (без образцов легенды)"""
    return {key: color for key, color in fake_driver.cell_colors.items() if _in_data(key)}


def test_xls_write_for_doubles(tmp_path: Any) -> None:
    """отчёт о дублях: группа первой колонкой, затем колонки внутреннего прайса, Дубль и Спорная"""
    row = {**write_data[0], 'group_by_params': 1, 'is_double': True, 'double_candidate': False}
    fake_driver = _write([row], tmp_path)
    now = datetime.datetime.now().strftime('%Y-%m-%d')

    assert fake_driver.file_name == f'doubles_{now}.xlsx'
    assert fake_driver.folder == str(tmp_path)
    assert fake_driver.head[0] == 'Группа по параметрам'
    assert fake_driver.head[-2:] == ['Дубль', 'Спорная']
    assert 'Главный дубль' not in fake_driver.head
    assert _data_cells(fake_driver) == {
        **{_shift(key): cell for key, cell in result_body_inner.items()},
        f'cell({_FIRST_ROW},{_GROUP_COL})': 1,
        f'cell({_FIRST_ROW},{_IS_DOUBLE_COL})': True,
    }


def test_xls_write_for_doubles_disputed(tmp_path: Any) -> None:
    """спорная группа дублей — колонка Спорная заполнена"""
    row = {**write_data[0], 'group_by_params': 1, 'is_double': True, 'disputed': 'шип'}
    fake_driver = _write([row], tmp_path)
    assert fake_driver.body[f'cell({_FIRST_ROW},{_DISPUTED_COL})'] == 'шип'


def test_xls_write_for_doubles_doubtful_row_is_red(tmp_path: Any) -> None:
    """сомнительный дубль — красятся все ячейки строки, обычный дубль — без цвета"""
    doubtful = {**write_data[0], 'group_by_params': 1, 'is_double': True, 'doubtful_price': True}
    plain = {**write_data[0], 'group_by_params': 1, 'is_double': True}
    colored = _data_colors(_write([doubtful, plain], tmp_path))
    assert set(colored.values()) == {'#ff9999'}
    assert all(key.startswith(f'cell({_FIRST_ROW},') for key in colored)
    assert len(colored) == _COLUMNS_IN_ROW


def test_xls_write_for_doubles_main_row_is_light_green(tmp_path: Any) -> None:
    """главный дубль — вся строка светло-зелёная"""
    main = {**write_data[0], 'group_by_params': 1, 'double_candidate': True}
    colored = _data_colors(_write([main], tmp_path))
    assert set(colored.values()) == {'#ccffcc'}
    assert len(colored) == _COLUMNS_IN_ROW - 1


def test_xls_write_for_doubles_writes_legend_above_head(tmp_path: Any) -> None:
    """над шапкой: образец цвета и пояснение, затем пустая строка"""
    fake_driver = _write([], tmp_path)
    for row_index, (color, text) in enumerate(_LEGEND):
        assert fake_driver.cell_colors[f'cell({row_index},0)'] == color
        assert fake_driver.body[f'cell({row_index},1)'] == text
