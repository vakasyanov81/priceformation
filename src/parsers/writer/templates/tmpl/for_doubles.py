"""
write template for duplicates report
"""

from typing import ClassVar

from domain.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import WriteColors, WriteColumns
from parsers.writer.templates.tmpl.for_inner import ForInner


class ForDoubles(ForInner):
    """write template for duplicates report"""

    __COLUMNS__: ClassVar[WriteColumns] = [
        *ForInner.__COLUMNS__,
        {'Группа по параметрам': {'field': RowItem.group_by_params.name}},
        {'Дубль': {'field': RowItem.is_double.name}},
        {'Главный дубль': {'field': RowItem.double_candidate.name}},
        {'Спорная': {'field': RowItem.disputed.name}},
    ]

    # Сомнительный дубль (цена отклоняется от главного на 5%+) — вся строка красным.
    __COLOR__: ClassVar[WriteColors] = {
        'by_column': RowItem.doubtful_price.name,
        'with_map': {True: '#ff9999'},
        'set_to_column_index': None,
    }

    __FILE__ = 'doubles_{now}.xlsx'
