"""ParseResultStatistic: min/max наценки после разбора."""

from parsers.base_item_actions.calc_percent_markup_item_action import SetPercentMarkupItemAction
from parsers.base_parser.parse_statistic import ParseResultStatistic
from parsers.row_item.row_item import RowItem

_PRICE = 100


def _row_with_zero_markup() -> RowItem:
    """Позиция как у Autosnab54: закупочная цена равна цене с наценкой."""
    row = RowItem({"price_opt": _PRICE, "price_markup": _PRICE})
    SetPercentMarkupItemAction(row).action()
    return row


def test_zero_percent_markup_min_max() -> None:
    """Несколько позиций с 0% наценкой: min/max не падают на None."""
    rows = [_row_with_zero_markup(), _row_with_zero_markup()]
    min_percent, max_percent = ParseResultStatistic(rows).real_percents_markup()
    assert min_percent == 0
    assert max_percent == 0
