"""
write template for duplicates report
"""

from parsers.row_item.row_item import RowItem
from parsers.writer.templates.tmpl.for_inner import ForInner


class ForDoubles(ForInner):
    """write template for duplicates report"""

    __COLUMNS__ = [
        *ForInner.__COLUMNS__,
        {"Группа по параметрам": {"field": RowItem.group_by_params.name}},
        {"Дубль": {"field": RowItem.is_double.name}},
        {"Главный дубль": {"field": RowItem.double_candidate.name}},
    ]

    __FILE__ = "doubles_{now}.xlsx"
