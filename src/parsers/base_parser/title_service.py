"""Название позиции: стратегия `title` или дефолтный фильтр, признаки из текста поставщика."""

from domain.row_item.markdown_title import is_markdown_title
from domain.row_item.production_plant import production_plant
from domain.row_item.production_year import production_year
from domain.row_item.row_item import RowItem
from parsers.base_parser.protocols import TitleFilterProtocol
from parsers.base_parser.strategy_hooks import StrategyHooks


class TitleService:
    """Подготовка title позиции и проверка его допустимости."""

    def __init__(self, hooks: StrategyHooks | None, title_filter: TitleFilterProtocol) -> None:
        self._hooks = hooks
        self.title_filter = title_filter

    def get_prepared_title(self, row_item: RowItem) -> str | None:
        """Подготовить title: стратегия или дефолт."""
        if self._hooks and self._hooks.title is not None:
            return self._hooks.title.prepare(row_item)
        return self.title_filter.get_prepared_title(row_item)

    def set_prepared_title(self, row_item: RowItem) -> bool:
        """Подготовить title; уценка, год и завод читаются и из текста поставщика: собранное название их не несёт."""
        source_title = row_item.identity.title
        prepared_title = self.get_prepared_title(row_item)
        title_is_prepared = source_title == prepared_title
        row_item.set_field('title', prepared_title or source_title)
        if is_markdown_title(source_title) or is_markdown_title(row_item.identity.title):
            row_item.set_field('marked_down', True)
        year = production_year(source_title) or production_year(row_item.identity.title)
        if year:
            row_item.set_field('production_year', year)
        plant = production_plant(source_title) or production_plant(row_item.identity.title)
        if plant:
            row_item.set_field('production_plant', plant)
        return title_is_prepared

    def is_valid_title(self, title: str | None) -> bool:
        return self.title_filter.is_valid_title(title)
