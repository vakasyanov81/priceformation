"""Производитель позиции: поиск в названии по алиасам из конфига."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.row_processor import apply_manufacturer
from parsers.base_parser.strategy_hooks import StrategyHooks


class ManufacturerService:
    """Поиск производителя в названии; включение при enrich задают `StrategyHooks` (без них — включён)."""

    def __init__(self, settings: ParserSettings, hooks: StrategyHooks | None) -> None:
        self._settings = settings
        self._hooks = hooks

    def apply_manufacturer(self, row_item: RowItem) -> None:
        find_on_enrich = True if self._hooks is None else self._hooks.find_manufacturer_on_enrich
        apply_manufacturer(row_item, find_on_enrich, self._settings.manufacturer_finder())

    def apply_manufacturer_after_pipeline(self, row_item: RowItem) -> None:
        """Найти производителя по финальному title, независимо от ``find_manufacturer_on_enrich``."""
        apply_manufacturer(row_item, True, self._settings.manufacturer_finder())
