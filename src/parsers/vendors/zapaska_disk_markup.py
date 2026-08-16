"""Markup helpers for zapaska disk parser."""

from typing import Optional, Tuple

from parsers.base_parser.price_markup import calc_percent, get_markup

_BASE_PERCENT = 0.12
_ABSOLUTE_MARKUP_DELTA = 150
MIN_RECOMMENDED_MARGIN_PERCENT = 0.08


def _percent_map() -> dict[tuple[int, int], float]:
    """Карта наценок по диапазонам цены."""
    step = 0.02
    return {
        (0, 5000): _BASE_PERCENT + step * 5,
        (5000, 10000): _BASE_PERCENT + step * 4,
        (10000, 15000): _BASE_PERCENT + step * 2,
        (15000, 20000): _BASE_PERCENT + step,
        (20000, 25000): _BASE_PERCENT,
    }


def _get_price_percent_markup(price: float) -> float:
    """get price percent markup"""
    for bounds, percent in _percent_map().items():
        if bounds[0] <= price < bounds[1]:
            return percent
    return _BASE_PERCENT


def make_absolute_markup(price: float, price_opt: float, delta: int = _ABSOLUTE_MARKUP_DELTA) -> float:
    """check price margin greater than delta"""
    if price - price_opt <= delta:
        return price_opt + delta
    return price


def _is_small_recommended_price(price_recommended: float, price_opt: float, percent: float) -> bool:
    """check margin for recommended price"""
    return bool(price_recommended and calc_percent(price_recommended, price_opt) <= percent)


def _make_price_recommended_markup(
    price_recommended: float,
    price_opt: float,
) -> Tuple[Optional[float], Optional[float]]:
    """make markup for recommended price"""
    if not price_recommended:
        return None, None

    percent = calc_percent(price_recommended, price_opt)

    # Если наценка менее 8% запускаем алгоритм наценки
    if not _is_small_recommended_price(price_recommended, price_opt, percent=MIN_RECOMMENDED_MARGIN_PERCENT):
        return price_recommended, percent

    percent = _get_price_percent_markup(price_opt)
    return get_markup(price_opt, percent), percent


def make_price_markup_value(price_recommended: float, price_opt: float) -> float:
    """Compute markup price from recommended and opt prices."""
    price, _ = _make_price_recommended_markup(price_recommended, price_opt)
    if not price:
        price = get_markup(price_opt, _get_price_percent_markup(price_opt))

    return make_absolute_markup(price, price_opt)
