"""
statistic for price formation result
"""

from dataclasses import dataclass, field

from domain.row_item.row_item import RowItem


@dataclass
class ParserStats:
    """Статистика работы парсера за один прогон: что и почему отбросили."""

    black_list_skips: int = 0
    unknown_category_skips: list[str] = field(default_factory=list)


class ParseResultStatistic:
    """
    statistic for price formation result
    """

    def __init__(self, parse_result: list[RowItem]) -> None:
        """init"""
        self._parse_result = [row_item for row_item in parse_result if row_item.pricing.price_opt]

    def real_percents_markup(self) -> tuple[float, float]:
        """real min / max percent markup for parse result"""
        if not self._parse_result:
            return 0, 0
        percents = [row_item.pricing.percent_markup or 0 for row_item in self._parse_result]
        return min(percents), max(percents)

    def real_absolute_markup(self) -> tuple[float, float]:
        """real absolute min / max markup for parse result"""
        if not self._parse_result:
            return 0, 0
        margins = [row_item.pricing.price_markup - row_item.pricing.price_opt for row_item in self._parse_result]
        return min(margins), max(margins)

    def count_items(self) -> int:
        """count parse result items"""
        if not self._parse_result:
            return 0
        return len(self._parse_result)
