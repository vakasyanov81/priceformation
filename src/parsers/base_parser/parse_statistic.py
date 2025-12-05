"""
statistic for price formation result
"""

from typing import List

from parsers.row_item.row_item import RowItem


class ParseResultStatistic:
    """
    statistic for price formation result
    """

    def __init__(self, parse_result: List[RowItem]):
        """init"""
        self._parse_result = [item for item in parse_result if item.price_opt]

    def real_percents_markup(self):
        """real min / max percent markup for parse result"""
        if not self._parse_result:
            return 0, 0
        percents = [item.percent_markup for item in self._parse_result]
        return min(percents), max(percents)

    def real_absolute_markup(self):
        """real absolute min / max markup for parse result"""
        if not self._parse_result:
            return 0, 0
        margins = [item.price_markup - item.price_opt for item in self._parse_result]
        return min(margins), max(margins)

    def count_items(self):
        """count parse result items"""
        if not self._parse_result:
            return 0
        return len(self._parse_result)
