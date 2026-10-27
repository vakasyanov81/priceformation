"""Подготовка строк после маппинга: title, фильтры по чёрному списку, производитель, категория, служебные поля."""

import logging

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_title import get_spike_title, replace_season
from parsers.base_parser.category_service import CategoryService
from parsers.base_parser.manufacturer_service import ManufacturerService
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.title_service import TitleService
from parsers.strategies.homoglyphs import fix_row_homoglyphs

logger = logging.getLogger(__name__)


def _log_row_parse_errors(supplier: str, row_id: int, row_item: RowItem) -> None:
    """Лог ошибок разбора полей строки."""
    logger.error(f'Не удалось разобрать строку (№ {row_id}) у поставщика: {supplier} // {row_item.parse_errors}')
    logger.error(f'строка: {row_item.to_dict()!r}')


class RowEnricher:
    """Разбор и отсев строк прайса; владеет сервисами title, категории и производителя."""

    def __init__(
        self,
        settings: ParserSettings,
        titles: TitleService,
        categories: CategoryService,
        manufacturers: ManufacturerService,
        stats: ParserStats,
    ) -> None:
        self._settings = settings
        self.titles = titles
        self.categories = categories
        self.manufacturers = manufacturers
        self._stats = stats

    def enrich(self, row_items: list[RowItem]) -> list[RowItem]:
        """Title, отсев по ошибкам/stop/black и служебные поля."""
        parsed_items: list[RowItem] = []
        start_row = self._settings.parser_params().start_row
        for row_id, row_item in enumerate(row_items, start=start_row):
            prepared = self._try_prepare_row(row_id, row_item)
            if prepared is not None:
                parsed_items.append(prepared)
        return parsed_items

    def keep(self, row_items: list[RowItem]) -> list[RowItem]:
        """Оставить строки с ценой закупки и валидным title."""
        return [row_item for row_item in row_items if self._keep_row_item(row_item)]

    def _keep_row_item(self, row_item: RowItem) -> bool:
        if row_item.stock.rest_count and not row_item.pricing.price_opt:
            return False
        if not row_item.identity.title or self.titles.is_valid_title(row_item.identity.title):
            return True
        self._stats.black_list_skips += 1
        return False

    def _try_prepare_row(self, row_id: int, row_item: RowItem) -> RowItem | None:
        """Подготовить одну строку или вернуть None при ошибке/фильтре."""
        homoglyphs = fix_row_homoglyphs(row_item)
        self._stats.homoglyph_fixes += len(homoglyphs.fixed)
        self._stats.homoglyph_suspects += len(homoglyphs.suspects)
        if not self._set_title_or_log(row_id, row_item):
            return None
        if row_item.parse_errors:
            _log_row_parse_errors(self._settings.title(), row_id, row_item)
            return None
        if not self.titles.is_valid_title(row_item.identity.title):
            if row_item.identity.title:
                self._stats.black_list_skips += 1
            return None
        return self._enrich_row_item(row_item)

    def _set_title_or_log(self, row_id: int, row_item: RowItem) -> bool:
        """Собрать title; при ValueError — лог и False."""
        try:
            self.titles.set_prepared_title(row_item)
        except ValueError as err:
            supplier = self._settings.title()
            logger.error(f'Не удалось разобрать строку (№ {row_id}) у поставщика: {supplier} // {err}')
            logger.error(f'строка: {row_item!r}')
            return False
        return True

    def _enrich_row_item(self, row_item: RowItem) -> RowItem:
        """Производитель, категория, служебные поля."""
        self.manufacturers.apply_manufacturer(row_item)
        self.categories.lookup.correction_category(row_item)
        row_item.set_field('supplier_name', self._settings.parser_params().supplier.name)
        row_item.set_field('spike', get_spike_title(row_item))
        row_item.set_field('season', replace_season(row_item))
        return row_item
