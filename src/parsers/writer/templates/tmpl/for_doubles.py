"""
write template for duplicates report
"""

from typing import ClassVar

from domain.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import WriteColors, WriteColumns
from parsers.writer.templates.tmpl.for_inner import ForInner

MAIN_DOUBLE_COLOR = '#ccffcc'
DOUBTFUL_COLOR = '#ff9999'


class ForDoubles(ForInner):
    """write template for duplicates report"""

    __COLUMNS__: ClassVar[WriteColumns] = [
        {'Группа по параметрам': {'field': RowItem.group_by_params.name}},
        *ForInner.__COLUMNS__,
        {'Дубль': {'field': RowItem.is_double.name}},
        {'Спорная': {'field': RowItem.disputed.name}},
    ]

    # Сомнительный дубль (цена отклоняется от главного на 5%+) — красным, главный дубль — светло-зелёным;
    # красим всю строку.
    __COLOR__: ClassVar[WriteColors] = {
        'rules': [
            {
                'by_column': RowItem.doubtful_price.name,
                'with_map': {True: DOUBTFUL_COLOR},
                'set_to_column_index': None,
            },
            {
                'by_column': RowItem.double_candidate.name,
                'with_map': {True: MAIN_DOUBLE_COLOR},
                'set_to_column_index': None,
            },
        ],
        'legend': [
            (MAIN_DOUBLE_COLOR, 'Главный дубль группы'),
            (DOUBTFUL_COLOR, 'Сомнительный дубль: цена отклоняется от главного на 5% и более'),
        ],
    }

    __FILE__ = 'doubles_{now}.xlsx'
