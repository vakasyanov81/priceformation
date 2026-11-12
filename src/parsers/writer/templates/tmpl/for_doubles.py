"""
write template for duplicates report
"""

from typing import ClassVar

from domain.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import WriteColors, WriteColumns
from parsers.writer.templates.tmpl.for_inner import DOUBLES_COLOR_RULES, DOUBLES_LEGEND, ForInner


class ForDoubles(ForInner):
    """write template for duplicates report"""

    template_id = 'for_doubles'

    __COLUMNS__: ClassVar[WriteColumns] = [
        {'Группа по параметрам': {'field': RowItem.group_by_params.name}},
        *ForInner.__COLUMNS__,
        {'Дубль': {'field': RowItem.is_double.name}},
        {'Спорная': {'field': RowItem.disputed.name}},
    ]

    # в отчёте дублей цвет поставщика не нужен — только подсветка дублей
    __COLOR__: ClassVar[WriteColors] = {'rules': DOUBLES_COLOR_RULES, 'legend': DOUBLES_LEGEND}

    __FILE__ = 'doubles_{now}.xlsx'
