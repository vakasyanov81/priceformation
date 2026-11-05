"""
tests write price for internal use
"""

import datetime
from typing import Any

from parsers.writer.row_style import RowColor, cell_color, row_colors
from parsers.writer.templates.tmpl.for_inner import ForInner
from parsers.writer.xls_writer import XlsWriter
from tests.fakes.fake_driver import FakeXlwtDriver

from .fixtures import result_body_inner, write_data


def test_xls_write_for_inner(tmp_path: Any) -> None:
    """test write price for internal use"""

    fake_driver = FakeXlwtDriver()
    result_folder = str(tmp_path)
    XlsWriter(
        fake_driver,
        write_data,
        template=ForInner,
        result_folder=result_folder,
    ).write()
    now = datetime.datetime.now().strftime('%Y-%m-%d')

    assert fake_driver.file_name == f'price_{now}.xlsx'
    assert fake_driver.folder == result_folder
    assert fake_driver.body == result_body_inner


def _row_cells(colors: list[RowColor]) -> list[str | None]:
    """цвета первой, второй и шестой ячейки строки"""
    indexes = (0, 1, 5)
    return [cell_color(colors, index) for index in indexes]


def test_inner_colors_supplier_first_cell_and_doubles_rest_of_row() -> None:
    """в общем прайсе первая ячейка — цвет поставщика, остальные — подсветка дублей, как в отчёте дублей"""
    template_colors = ForInner().colors()
    main = row_colors(template_colors, {'double_candidate': True, 'supplier_name': 'Мим'})
    assert _row_cells(main) == ['#f7d5d2', '#ccffcc', '#ccffcc']
    doubtful = row_colors(template_colors, {'doubtful_price': True, 'double_candidate': True, 'supplier_name': 'Мим'})
    assert _row_cells(doubtful) == ['#f7d5d2', '#ff9999', '#ff9999']
    plain = row_colors(template_colors, {'supplier_name': 'Мим'})
    assert _row_cells(plain) == ['#f7d5d2', None, None]
    assert 'legend' not in template_colors
