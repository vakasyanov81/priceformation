"""Ядро BaseParser: состояние, доступ к конфигу, имя поставщика."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import ParseConfigNotSetError, ParseConfiguration, ParserParams
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.base_parser.manufacturer_finder import ManufacturerFinder
from parsers.base_parser.markup_policy import MarkupPolicySpec
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.protocols import FileReaderProtocol, RowProcessorProtocol, TitleFilterProtocol
from parsers.base_parser.row_processor import RowProcessor
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.base_parser.title_filter import TitleFilter
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
        self._parse_config = parse_config
        self._strategy_hooks = strategy_hooks
        self.type_production: str | None = None
        self.data_reader = data_reader or XlsReader
        self.files: list[str] | None = None
        self.logger = LoggerParseProcess(repr(self))  # raises ParseConfigNotSetError if config is None
        self._category_finder: CategoryFinder | None = None
        self._manufacturer_finder: ManufacturerFinder | None = None
        self.stats = ParserStats()

        self._file_reader_impl = file_reader or FileReader(data_reader=self.data_reader)
        self._row_processor = row_processor or RowProcessor()
        self._title_filter = title_filter or TitleFilter(self._parse_config)

    def parse_config(self) -> ParseConfiguration:
        if self._parse_config is None:
            raise ParseConfigNotSetError()
        return self._parse_config

    def set_parse_config(self, parse_config: ParseConfiguration) -> None:
        self._parse_config = parse_config
        self._manufacturer_finder = None
        self._title_filter.reset_caches()

    def parser_params(self) -> ParserParams:
        return self.parse_config().parser_params

    def manufacturer_finder(self) -> ManufacturerFinder:
        if self._manufacturer_finder is None:
            aliases = self.parse_config().manufacturer_aliases()
            self._manufacturer_finder = ManufacturerFinder(aliases)
        return self._manufacturer_finder

    @property
    def is_active(self) -> bool:
        vendor_cfg = getattr(self._parse_config, '_vendor_config', None)
        if vendor_cfg is not None:
            return bool(vendor_cfg.enabled)
        # Fallback для легаси-вендоров
        return True

    def __repr__(self) -> str:
        """Название поставщика из конфига; имя класса (BaseParser) не показываем."""
        supplier_name = self.parser_params().supplier.name
        sheet_info = self.parser_params().sheet_info
        if sheet_info:
            return f'{supplier_name} ({sheet_info})'
        return supplier_name
