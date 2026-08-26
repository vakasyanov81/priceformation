"""Percent and absolute markup arithmetic."""

from parsers.row_item.row_item import RowItem


def calc_percent(price_sale: float, price_purchase: float) -> float:
    """Margin as a fraction of purchase price."""
    return (price_sale - price_purchase) / price_purchase


def get_markup(price: float, percent: float) -> float:
    """Price with percent markup applied."""
    return price * (1 + percent)


def recommended_percent(price_opt: float, price_recommended: float | None) -> float:
    """Доля РРЦ к закупу. 0 если РРЦ нет."""
    recommended = price_recommended or 0
    opt = price_opt or 0
    return calc_percent(recommended, opt) if recommended else 0


def fill_percent_markup(row_items: list[RowItem]) -> None:
    """Записать percent_markup из цен, если его ещё нет (Poshk/Pioner уже пишут сами)."""
    for row_item in row_items:
        if row_item.percent_markup or not row_item.price_markup:
            continue
        fraction = calc_percent(row_item.price_markup, row_item.price_opt)
        row_item.percent_markup = round(fraction * 100, 2)
