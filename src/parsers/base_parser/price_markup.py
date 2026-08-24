"""Percent and absolute markup arithmetic."""


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
