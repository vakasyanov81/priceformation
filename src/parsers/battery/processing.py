"""Условия публикации аккумулятора и диагностика исключённых предложений."""

import logging

from domain.battery.item import BatteryItem

logger = logging.getLogger(__name__)


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
