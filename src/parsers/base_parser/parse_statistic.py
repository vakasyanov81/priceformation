"""
statistic for price formation result
"""

from typing import List, Tuple

from parsers.row_item.row_item import RowItem


class ParseResultStatistic:
    """
    statistic for price formation result
    """

    def __init__(self, parse_result: List[RowItem]) -> None:
        """init"""
        self._parse_result = [row_item for row_item in parse_result if row_item.price_opt]

    def real_percents_markup(self) -> Tuple[float, float]:
        """real min / max percent markup for parse result"""
        if not self._parse_result:
            return 0, 0
        percents = [row_item.percent_markup for row_item in self._parse_result]
        return min(percents), max(percents)

    def real_absolute_markup(self) -> Tuple[float, float]:
        """real absolute min / max markup for parse result"""
        if not self._parse_result:
            return 0, 0
        margins = [row_item.price_markup - row_item.price_opt for row_item in self._parse_result]
        return min(margins), max(margins)

    def count_items(self) -> int:
        """count parse result items"""
        if not self._parse_result:
            return 0
        return len(self._parse_result)
