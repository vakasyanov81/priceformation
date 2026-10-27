"""base parser logic — composition of FileReader, RowProcessor, TitleFilter.

Роли разложены по цепочке слоёв (``parser_core`` → … → ``parser_pipeline``), чтобы каждый
класс укладывался в лимит методов; ``BaseParser`` собирает их и ведёт основной pipeline.
"""

from typing import Any, Protocol

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.base_parser_row import _keep_row_item, drop_empty_rest, enrich_items
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.markup_policy import MarkupPolicy, make_markup_policy
from parsers.base_parser.parse_statistic import ParseResultStatistic
from parsers.base_parser.parser_pipeline import ParserPipeline
from parsers.base_parser.price_markup import fill_absolute_markup, fill_percent_markup
from parsers.base_parser.row_processor import RowProcessor


class Parser(Protocol):
    """parser protocol"""

    @classmethod
    def supplier_folder_name(cls) -> str: ...

    def get_parsed_items(self) -> list[RowItem]: ...

    def parse(self) -> list[RowItem]: ...


class BaseParser(ParserPipeline):
    """Парсер — композиция FileReader, RowProcessor, TitleFilter."""

    def parse(self) -> list[RowItem]:
        if not self.settings.is_active:
            self.logger.log_disable_status()
            return []
        self._category_finder = CategoryFinder()
        self.files = self._price_files()
        self.logger.log_start()
        self.process()
        self.after_process()
        parsed = self.get_parsed_items()
        self.logger.log_finish(ParseResultStatistic(parsed))
        return parsed

    def process(self) -> int:
        """read → map → filter → enrich → vendor hook. Count before filters."""
        files = self.files or []
        self.logger.log_list_files(files)
        mapped = self.map_items(self.read_rows(files))
        raw_count = len(mapped)
        self.parsed_items += mapped
        self.parsed_items = self.filter_warehouses(self.parsed_items)
        self.parsed_items = self.filter_keep(self.parsed_items)
        self.parsed_items = self.enrich(self.parsed_items)
        self.apply_vendor_hooks(self.parsed_items)
        return raw_count

    def after_process(self) -> None:
        self.parsed_items = drop_empty_rest(self.parsed_items)
        fill_percent_markup(self.parsed_items)
        fill_absolute_markup(self.parsed_items)
        self.stats.type_corrections = self.count_type_corrections()
        self.stats.title_conflicts = sum(1 for row_item in self.parsed_items if row_item.vendor.title_conflict)
        self.stats.titles_not_composed = sum(1 for row_item in self.parsed_items if row_item.vendor.title_not_composed)

    def count_type_corrections(self) -> int:
        """Число позиций итогового результата с исправленным типом.

        Считается после ``drop_empty_rest``: расхождения у позиций, отброшенных
        без цены закупки или остатка, в прайс не попадают и в счётчик не входят.
        """
        return sum(1 for row_item in self.parsed_items if row_item.vendor.type_corrected)

    def enrich(self, row_items: list[RowItem]) -> list[RowItem]:
        return enrich_items(self, row_items)

    def filter_keep(self, row_items: list[RowItem]) -> list[RowItem]:
        return [row_item for row_item in row_items if _keep_row_item(self, row_item)]


def make_parser[TParser: BaseParser](
    parser_cls: type[TParser],
    parse_config: ParseConfiguration,
    *,
    markup_policy: MarkupPolicy | None = None,
    file_prices: list[str] | None = None,
    data_reader: type[Any] | None = None,
) -> TParser:
    """Собрать парсер с политикой наценки. Не метод BaseParser."""
    policy = make_markup_policy(parse_config) if markup_policy is None else markup_policy
    kwargs: dict[str, Any] = {
        'parse_config': parse_config,
        'row_processor': RowProcessor(markup_policy=policy),
    }
    if data_reader is not None:
        kwargs['data_reader'] = data_reader
    parser = parser_cls(**kwargs)
    parser.files = file_prices
    return parser
