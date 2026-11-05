"""
tests write price for internal use
"""

import datetime
from typing import Any

from parsers.writer.row_style import row_color
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


def test_inner_colors_doubles_whole_row_and_suppliers_first_cell() -> None:
    """в общем прайсе дубли красятся как в отчёте дублей, остальные — цветом поставщика в первой ячейке"""
    colors = ForInner().colors()
    assert row_color(colors, {'double_candidate': True, 'supplier_name': 'Мим'}) == ('#ccffcc', None)
    assert row_color(colors, {'doubtful_price': True, 'double_candidate': True}) == ('#ff9999', None)
    assert row_color(colors, {'supplier_name': 'Мим'}) == ('#f7d5d2', 0)
    assert 'legend' not in colors
