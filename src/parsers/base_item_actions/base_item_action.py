"""
base item action logic
"""

from parsers.row_item.row_item import RowItem


class BaseItemAction:
    """Abstract base price item action"""

    def __init__(self, row_item: RowItem) -> None:
        """init"""
        self.row_item = row_item

    def action(self) -> RowItem:
        """action logic"""
        raise NotImplementedError
