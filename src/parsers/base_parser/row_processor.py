"""Пошаговая обработка строк: остатки, наценка, производитель, категории.

Дефолтная логика для методов-хуков BaseParser. Хуки, которые вендоры
переопределяют на классе парсера (get_item_rest, get_min_rest_count и т.д.),
остаются на BaseParser, а RowProcessor держит чистые реализации.
"""

from typing import Any

from parsers.base_parser.markup_policy import IdentityMarkupPolicy, MarkupPolicy, percent_to_store
from parsers.row_item.row_item import RowItem

_CENTS_STEP = 10


class MarkupPolicyNotSetError(RuntimeError):
    """Raised when markup is used before MarkupPolicy is injected."""

    def __init__(self) -> None:
        super().__init__('markup_policy is not set')


def apply_min_rest(row_item: RowItem, rest: Any, min_rest: int) -> None:
    """Обнулить остаток, если он меньше минимального."""
    if rest is None or rest < min_rest:
        row_item.rest_count = 0


def apply_manufacturer(row_item: RowItem, find_on_enrich: bool, manufacturer_finder: Any) -> None:
    """Применить производителя, если включено."""
    if find_on_enrich:
        manufacturer_finder.process(row_item)


def correction_category(row_item: RowItem, category_finder: Any) -> None:
    """Скорректировать категорию, если найдена плохая."""
    if not row_item.type_production or category_finder is None:
        return
    category, bad_category = category_finder.find_in_str(row_item.type_production)
    if bad_category:
        row_item.type_production = category


class RowProcessor:  # noqa: WPS214
    """Дефолтные реализации построжечной обработки: остатки, наценка, производитель.

    Содержит только instance-методы, требующие self._markup_policy.
    Все чистые утилиты вынесены в модульные функции.
    """

    def __init__(self, markup_policy: MarkupPolicy | None = None) -> None:
        self._markup_policy = markup_policy

    def _require_markup_policy(self) -> MarkupPolicy:
        if self._markup_policy is None:
            raise MarkupPolicyNotSetError()
        return self._markup_policy

    def get_markup_percent(self, price_value: float) -> float:
        return self._require_markup_policy().markup_percent_for_opt(price_value)

    def add_price_markup(self, row_item: RowItem) -> None:
        policy = self._require_markup_policy()
        opt = row_item.price_opt or 0
        price = policy.apply(opt, row_item.price_recommended)
        if isinstance(policy, IdentityMarkupPolicy):
            row_item.price_markup = price
        else:
            row_item.price_markup = -(-price // _CENTS_STEP) * _CENTS_STEP
        percent = percent_to_store(policy, opt)
        if percent is not None:
            row_item.percent_markup = percent
