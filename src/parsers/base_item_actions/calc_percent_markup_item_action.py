"""
price markup action
"""

from .base_item_action import BaseItemAction


class SetPercentMarkupItemAction(BaseItemAction):
    """Calculate percent markup"""

    __description__ = "Calculate percent markup"

    def action(self):
        """
        calculate percent markup
        """

        if self.calculated:
            self.item.percent_markup = self.markup_percent

        return self.item

    @property
    def already_calculated(self):
        """already calculated"""
        return self.item.percent_markup

    @property
    def empty_price_markup(self):
        """has not price markup value"""
        return not self.item.price_markup

    @property
    def calculated(self):
        """validation"""
        return not (self.already_calculated or self.empty_price_markup)

    @property
    def markup(self):
        """calculate markup"""
        return (self.item.price_markup / self.item.price_opt) - 1

    @property
    def markup_percent(self):
        """calculate markup percent"""
        return round(self.markup * 100, 2)
