"""
base parser logic
"""

from typing import Protocol

from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.base_parser_reader import ParserFileReader, ReaderFactory
from parsers.base_parser.base_parser_row import _keep_row_item, drop_empty_rest, enrich_items
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.base_parser.markup_policy import MarkupPolicy, make_markup_policy
from parsers.base_parser.parse_statistic import ParseResultStatistic
from parsers.base_parser.price_markup import fill_percent_markup
from parsers.base_parser.price_source import FilePricesSource, PriceSource
from parsers.row_item.row_item import RowItem
from parsers.xls_reader import XlsReader


class Parser(Protocol):
    """parser protocol"""

    @classmethod
    def supplier_folder_name(cls) -> str:
        """supplier folder name"""
        ...

    def get_parsed_items(self) -> list[RowItem]:
        """get parsed items"""
        ...

    def parse(self) -> list[RowItem]:
        """parse price files"""
        ...


class BaseParser(ParserFileReader):
    def __init__(
        self,
        parse_config: ParseConfiguration | None = None,
        file_prices: list[str] | None = None,
        data_reader: type[ReaderFactory] = XlsReader,
        *,
        markup_policy: MarkupPolicy | None = None,
        price_source: PriceSource | None = None,
    ) -> None:
        self.parsed_items: list[RowItem] = []
        self._parse_config = parse_config
        self.type_production: str | None = None
        self.data_reader = data_reader
        self.files: list[str] | None = file_prices
        self.logger = LoggerParseProcess(repr(self))
        self._black_list: list[str] | None = None
        self._stop_words: list[str] | None = None
        self._category_finder: CategoryFinder | None = None
        self._manufacturer_finder = None
        self.unknown_category_skips: list[str] = []
        self.black_list_skips = 0
        self._markup_policy = markup_policy
        self._price_source = price_source or FilePricesSource()

    def parse(self) -> list[RowItem]:
        if not self.is_active:
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
        self.parsed_items = self.filter_keep(self.parsed_items)
        self.parsed_items = self.enrich(self.parsed_items)
        self.apply_vendor_hooks(self.parsed_items)
        return raw_count

    def after_process(self) -> None:
        """drop empty rest → fill percent markup."""
        self.parsed_items = drop_empty_rest(self.parsed_items)
        fill_percent_markup(self.parsed_items)

    def enrich(self, row_items: list[RowItem]) -> list[RowItem]:
        return enrich_items(self, row_items)

    def filter_keep(self, row_items: list[RowItem]) -> list[RowItem]:
        return [row_item for row_item in row_items if _keep_row_item(self, row_item)]

    def apply_vendor_hooks(self, row_items: list[RowItem]) -> None:
        for row_item in row_items:
            self.process_parsed_row(row_item)


def make_parser[TParser: BaseParser](
    parser_cls: type[TParser],
    parse_config: ParseConfiguration,
    *,
    markup_policy: MarkupPolicy | None = None,
    file_prices: list[str] | None = None,
    data_reader: type[ReaderFactory] | None = None,
) -> TParser:
    """Собрать парсер с политикой наценки. Не метод BaseParser."""
    policy = make_markup_policy(parse_config) if markup_policy is None else markup_policy
    if data_reader is None:
        return parser_cls(
            parse_config=parse_config,
            file_prices=file_prices,
            markup_policy=policy,
        )
    return parser_cls(
        parse_config=parse_config,
        file_prices=file_prices,
        data_reader=data_reader,
        markup_policy=policy,
    )
