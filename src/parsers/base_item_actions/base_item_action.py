"""
base item action logic
"""

from parsers.row_item.row_item import RowItem


class BaseItemAction:
    """Abstract base price item action"""

    def __init__(self, row_item: RowItem):
        """init"""
        self.row_item = row_item

    def action(self):
        """action logic"""
        raise NotImplementedError
