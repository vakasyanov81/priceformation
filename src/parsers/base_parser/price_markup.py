"""Percent and absolute markup arithmetic."""


def calc_percent(price_sale: float, price_purchase: float) -> float:
    """Margin as a fraction of purchase price."""
    return (price_sale - price_purchase) / price_purchase


def get_markup(price: float, percent: float) -> float:
    """Price with percent markup applied."""
    return price * (1 + percent)
