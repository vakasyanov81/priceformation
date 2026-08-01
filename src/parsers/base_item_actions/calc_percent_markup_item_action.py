"""
price markup action
"""

from parsers.row_item.row_item import RowItem

from .base_item_action import BaseItemAction


class SetPercentMarkupItemAction(BaseItemAction):
    """Calculate percent markup"""

    __description__ = "Calculate percent markup"

    def action(self) -> RowItem:
        """
        calculate percent markup
        """

        if self.calculated:
            self.row_item.percent_markup = self.markup_percent

        return self.row_item

    @property
    def already_calculated(self) -> float | None:
        """already calculated"""
        return self.row_item.percent_markup

    @property
    def empty_price_markup(self) -> bool:
        """has not price markup value"""
        return not self.row_item.price_markup

    @property
    def calculated(self) -> bool:
        """validation"""
        return not (self.already_calculated or self.empty_price_markup)

    @property
    def markup(self) -> float:
        """calculate markup"""
        return (self.row_item.price_markup / self.row_item.price_opt) - 1

    @property
    def markup_percent(self) -> float:
        """calculate markup percent"""
        return round(self.markup * 100, 2)
