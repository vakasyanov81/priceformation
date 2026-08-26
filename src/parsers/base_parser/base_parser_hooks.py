"""Markup, rest filter and vendor-row hooks."""

import math
from typing import Any, ClassVar

from parsers.base_parser import price_markup
from parsers.base_parser.base_parser_title import ParserTitleFilters
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.markup_policy import IdentityMarkupPolicy, MarkupPolicy, percent_to_store
from parsers.row_item.row_item import RowItem

_CENTS_STEP = 10
_MIN_REST_COUNT = 4


class MarkupPolicyNotSetError(RuntimeError):
    """Raised when markup is used before MarkupPolicy is injected."""

    def __init__(self) -> None:
        super().__init__("markup_policy is not set")


class ParserMarkupOps(ParserTitleFilters):
    _markup_policy: MarkupPolicy | None

    def get_markup_percent(self, price_value: float) -> float:
        return self._require_markup_policy().markup_percent_for_opt(price_value)

    def add_price_markup(self, row_item: RowItem) -> None:
        """calculate and fill price_markup field"""
        policy = self._require_markup_policy()
        opt = row_item.price_opt or 0
        price = policy.apply(opt, row_item.price_recommended)
        if isinstance(policy, IdentityMarkupPolicy):
            row_item.price_markup = price
        else:
            row_item.price_markup = self.round_price(price)
        percent = percent_to_store(policy, opt)
        if percent is not None:
            row_item.percent_markup = percent

    def _require_markup_policy(self) -> MarkupPolicy:
        if self._markup_policy is None:
            raise MarkupPolicyNotSetError()
        return self._markup_policy

    @classmethod
    def round_price(cls, price_value: float) -> float:
        """rounding to cents"""
        return math.ceil(price_value / _CENTS_STEP) * _CENTS_STEP

    @classmethod
    def get_markup(cls, price: float, percent: float) -> float:
        """get price with absolute markup"""
        return price_markup.get_markup(price, percent)


class ParserRestPolicy(ParserMarkupOps):
    @classmethod
    def get_min_rest_count(cls) -> int:
        return _MIN_REST_COUNT

    @classmethod
    def get_item_rest(cls, row_item: RowItem) -> Any:
        return row_item.rest_count

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        rest = self.get_item_rest(row_item)
        if rest is None or rest < self.get_min_rest_count():
            row_item.rest_count = 0

    @classmethod
    def is_category_row(cls, row_item: RowItem) -> bool:
        """is category row?"""
        return bool(row_item.title and not row_item.price_opt)


class ParserRowHooks(ParserRestPolicy):
    find_manufacturer_on_enrich: ClassVar[bool] = True
    _category_finder: CategoryFinder | None

    def apply_manufacturer(self, row_item: RowItem) -> None:
        if self.find_manufacturer_on_enrich:
            self.manufacturer_finder().process(row_item)

    def after_row_mapped(self, row_item: RowItem) -> None:
        """Редкое уникальное после enrich (title, fill_from_title). По умолчанию ничего."""

    def category_for(self, row_item: RowItem) -> str | None:
        """Категория строки. None — не менять type_production."""

    def apply_category(self, row_item: RowItem) -> None:
        category = self.category_for(row_item)
        if category is not None:
            row_item.type_production = category

    def process_parsed_row(self, row_item: RowItem) -> None:
        """После enrich: уникальное, min rest, категория, наценка."""
        self.after_row_mapped(row_item)
        self.skip_by_min_rest(row_item)
        self.apply_category(row_item)
        self.add_price_markup(row_item)

    def correction_category(self, row_item: RowItem) -> None:
        if not row_item.type_production or self._category_finder is None:
            return
        category, bad_category = self._category_finder.find_in_str(row_item.type_production)
        if bad_category:
            row_item.type_production = category
