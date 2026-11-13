"""Условия публикации аккумулятора и диагностика исключённых предложений."""

import logging
from dataclasses import replace
from decimal import Decimal

from domain.battery.item import BatteryItem
from parsers.base_parser.markup_policy import MarkupPolicy

logger = logging.getLogger(__name__)


def apply_markup(position: BatteryItem, policy: MarkupPolicy) -> BatteryItem:
    """Если РРЦ не выше закупа, применить карту процентов, сохраняя исходные цены."""
    offer = position.offer
    price = offer.price_recommended
    if offer.price_opt is not None and price is not None and price <= offer.price_opt:
        percent = Decimal(str(policy.markup_percent_for_opt(float(offer.price_opt))))
        price = (offer.price_opt * (1 + percent)).normalize()
    return replace(position, offer=replace(offer, price_markup=price))


def publication_issue(position: BatteryItem, min_rest: int) -> str | None:
    """Не подставлять закупочную цену или шинный порог при отсутствии аккумуляторных данных."""
    issue = _required_issue(position)
    if issue is not None:
        return issue
    stock = position.offer.rest_count
    if stock is None or stock < min_rest:
        return f'остаток {stock} меньше минимального {min_rest}'
    return None


def log_skipped(position: BatteryItem, supplier: str, issue: str) -> None:
    """У каждой диагностики есть группа, поставщик и код исходной позиции."""
    logger.warning('[batteries] %s, код %s: %s', supplier, position.identity.code, issue)


def _required_issue(position: BatteryItem) -> str | None:
    """Наличие РРЦ проверяется отдельно от её величины: нулевая цена не означает неизвестную."""
    required = {
        'code': position.identity.code,
        'title': position.identity.title,
        'price_recommended': position.offer.sale_price,
    }
    missing = [key for key, field_value in required.items() if field_value is None]
    if missing:
        fields = ', '.join(missing)
        return f'отсутствуют обязательные поля: {fields}'
    return None
