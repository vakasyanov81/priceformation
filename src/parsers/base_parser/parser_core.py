"""Ядро BaseParser: состояние, доступ к конфигу, имя поставщика."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.base_parser.markup_policy import MarkupPolicySpec
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.protocols import FileReaderProtocol, RowProcessorProtocol, TitleFilterProtocol
from parsers.base_parser.row_filters import RowFilters
from parsers.base_parser.row_processor import RowProcessor
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.base_parser.title_filter import TitleFilter
from parsers.base_parser.title_service import TitleService
from parsers.xls_reader import XlsReader


class ParserCore:
    """Состояние парсера и доступ к конфигу; нижний слой цепочки ролей BaseParser."""

    find_manufacturer_on_enrich: bool = True
    _markup_policy_type: MarkupPolicySpec | None = None

    def __init__(
        self,
        parse_config: ParseConfiguration | None = None,
        *,
        file_reader: FileReaderProtocol | None = None,
        data_reader: type[Any] | None = None,
        row_processor: RowProcessorProtocol | None = None,
        title_filter: TitleFilterProtocol | None = None,
        strategy_hooks: StrategyHooks | None = None,
    ) -> None:
        self.parsed_items: list[RowItem] = []
        self.settings = ParserSettings(parse_config)
        self._strategy_hooks = strategy_hooks
        self.row_filters = RowFilters(strategy_hooks)
        self.data_reader = data_reader or XlsReader
        self.logger = LoggerParseProcess(repr(self))  # raises ParseConfigNotSetError if config is None
        self._category_finder: CategoryFinder | None = None
        self.stats = ParserStats()

        self.price_files = PriceFiles(self.settings, file_reader or FileReader(data_reader=self.data_reader))
        self._row_processor = row_processor or RowProcessor()
        self.titles = TitleService(strategy_hooks, title_filter or TitleFilter(parse_config))

    def __repr__(self) -> str:
        """Название поставщика из конфига; имя класса (BaseParser) не показываем."""
        return self.settings.title()
