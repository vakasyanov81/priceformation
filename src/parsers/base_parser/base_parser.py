"""Парсер поставщика: тонкий оркестратор над коллабораторами (настройки, файлы, фильтры, enrich, pipeline)."""

from typing import Any, Protocol

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.price_source import FilePricesSource
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.base_parser.markup_policy import MarkupPolicy, make_markup_policy
from parsers.base_parser.parse_statistic import ParserStats, ParseResultStatistic
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.price_markup import fill_absolute_markup, fill_percent_markup
from parsers.base_parser.protocols import FileReaderProtocol, RowProcessorProtocol, TitleFilterProtocol
from parsers.base_parser.row_enricher import make_row_enricher
from parsers.base_parser.row_filters import RowFilters, drop_empty_rest
from parsers.base_parser.row_pipeline import RowPipeline
from parsers.base_parser.row_processor import RowProcessor
from parsers.base_parser.strategy_hooks import StrategyHooks


class Parser(Protocol):
    """parser protocol"""

    @classmethod
    def supplier_folder_name(cls) -> str: ...

    def get_parsed_items(self) -> list[RowItem]: ...

    def parse(self) -> list[RowItem]: ...


def _default_file_reader(settings: ParserSettings, data_reader: type[Any] | None) -> FileReader:
    """Читатель прайсов с источником файлов на диске, путь к которому даёт провайдер конфига."""
    price_source = FilePricesSource(settings.parse_config().config_provider)
    return FileReader(data_reader=data_reader, price_source=price_source)


class BaseParser:
    """Парсер поставщика: оркестратор, который ведёт `parse` по коллабораторам."""

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
        self._logger = LoggerParseProcess(repr(self))  # raises ParseConfigNotSetError if config is None
        self.stats = ParserStats()
        self.price_files = PriceFiles(self.settings, file_reader or _default_file_reader(self.settings, data_reader))
        self.row_filters = RowFilters(strategy_hooks)
        self.enricher = make_row_enricher(self.settings, self.stats, strategy_hooks, title_filter)
        self.pipeline = RowPipeline(strategy_hooks, self.row_filters, self.enricher, row_processor or RowProcessor())

    def __repr__(self) -> str:
        """Название поставщика из конфига; имя класса (BaseParser) не показываем."""
        return self.settings.title()

    def parse(self) -> list[RowItem]:
        if not self.settings.is_active:
            self._logger.log_disable_status()
            return []
        self.enricher.categories.lookup.reset()
        self.price_files.resolve()
        self._logger.log_start()
        self.process()
        self.after_process()
        parsed = self.get_parsed_items()
        self._logger.log_finish(ParseResultStatistic(parsed))
        return parsed

    def get_parsed_items(self) -> list[RowItem]:
        return self.parsed_items

    def process(self) -> int:
        """read → map → filter → enrich → vendor hook. Count before filters."""
        files = self.price_files.files or []
        self._logger.log_list_files(files)
        mapped = self.price_files.map_items(self.price_files.read_rows(files))
        raw_count = len(mapped)
        self.parsed_items += mapped
        self.parsed_items = self.row_filters.filter_warehouses(self.parsed_items)
        self.parsed_items = self.enricher.keep(self.parsed_items)
        self.parsed_items = self.enricher.enrich(self.parsed_items)
        self.pipeline.run(self.parsed_items)
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
    parser.price_files.files = file_prices
    return parser
