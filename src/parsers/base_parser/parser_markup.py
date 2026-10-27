"""Производитель и наценка в BaseParser (делегирует RowProcessor и markup_policy)."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.base_parser.parser_category import ParserCategory
from parsers.base_parser.price_markup import get_markup as price_get_markup
from parsers.base_parser.row_processor import apply_manufacturer as apply_row_manufacturer

_CENTS = 10


class ParserManufacturer(ParserCategory):
    """Поиск производителя в названии позиции."""

    @property
    def _effective_find_manufacturer(self) -> bool:
        """``find_manufacturer_on_enrich`` с учётом стратегий."""
        if self._strategy_hooks is not None:
            return self._strategy_hooks.find_manufacturer_on_enrich
        return self.find_manufacturer_on_enrich

    def apply_manufacturer(self, row_item: RowItem) -> None:
        apply_row_manufacturer(row_item, self._effective_find_manufacturer, self.settings.manufacturer_finder())

    def apply_manufacturer_after_pipeline(self, row_item: RowItem) -> None:
        """Найти производителя по финальному title, независимо от ``find_manufacturer_on_enrich``."""
        apply_row_manufacturer(row_item, True, self.settings.manufacturer_finder())


class ParserMarkup(ParserManufacturer):
    """Наценка и округление цены."""

    def add_price_markup(self, row_item: RowItem) -> None:
        self._row_processor.add_price_markup(row_item)

    def get_markup_percent(self, price_value: float) -> float:
        return self._row_processor.get_markup_percent(price_value)

    @classmethod
    def round_price(cls, price_value: float) -> float:
        return -(-price_value // _CENTS) * _CENTS

    @classmethod
    def get_markup(cls, price: float, percent: float) -> float:
        return price_get_markup(price, percent)

    def require_markup_policy(self) -> MarkupPolicy:
        return self._row_processor.require_markup_policy()
