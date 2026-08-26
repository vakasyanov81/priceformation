"""ParseResultStatistic: min/max наценки после разбора."""

from parsers.base_parser.parse_statistic import ParseResultStatistic
from parsers.base_parser.price_markup import fill_percent_markup
from parsers.row_item.row_item import RowItem

_PRICE = 100


def _row_with_zero_markup() -> RowItem:
    """Позиция как у Autosnab54: закупочная цена равна цене с наценкой."""
    row = RowItem({"price_opt": _PRICE, "price_markup": _PRICE})
    fill_percent_markup([row])
    return row


_OPT = 100
_MARKUP_LOW = 130
_MARKUP_HIGH = 180
_PERCENT = 30
_MARGIN_LOW = 30
_MARGIN_HIGH = 80


def test_zero_percent_markup_min_max() -> None:
    """Несколько позиций с 0% наценкой: min/max не падают на None."""
    rows = [_row_with_zero_markup(), _row_with_zero_markup()]
    min_percent, max_percent = ParseResultStatistic(rows).real_percents_markup()
    assert min_percent == 0
    assert max_percent == 0


def test_empty_statistic_zeros() -> None:
    stats = ParseResultStatistic([])
    assert stats.real_percents_markup() == (0, 0)
    assert stats.real_absolute_markup() == (0, 0)
    assert stats.count_items() == 0


def test_percent_markup_uses_stored_value() -> None:
    row = RowItem({"price_opt": _OPT, "price_markup": _MARKUP_LOW, "percent_markup": _PERCENT})
    assert ParseResultStatistic([row]).real_percents_markup() == (_PERCENT, _PERCENT)


def test_absolute_markup_min_max() -> None:
    cheap = RowItem({"price_opt": _OPT, "price_markup": _MARKUP_LOW})
    pricey = RowItem({"price_opt": _OPT, "price_markup": _MARKUP_HIGH})
    min_margin, max_margin = ParseResultStatistic([cheap, pricey]).real_absolute_markup()
    assert min_margin == _MARGIN_LOW
    assert max_margin == _MARGIN_HIGH


def test_count_items_with_purchase_price() -> None:
    rows = [RowItem({"price_opt": _OPT, "price_markup": _MARKUP_LOW})]
    assert ParseResultStatistic(rows).count_items() == 1


def test_fill_percent_keeps_stored_value() -> None:
    row = RowItem({"price_opt": _OPT, "price_markup": _MARKUP_LOW, "percent_markup": _PERCENT})
    fill_percent_markup([row])
    assert row.percent_markup == _PERCENT


def test_fill_percent_from_prices() -> None:
    row = RowItem({"price_opt": _OPT, "price_markup": _MARKUP_LOW})
    fill_percent_markup([row])
    assert row.percent_markup == _PERCENT


def test_fill_percent_skips_empty_markup() -> None:
    row = RowItem({"price_opt": _OPT})
    fill_percent_markup([row])
    assert not row.percent_markup
