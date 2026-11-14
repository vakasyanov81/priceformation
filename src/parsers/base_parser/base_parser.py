"""Парсер поставщика: тонкий оркестратор над коллабораторами (настройки, файлы, фильтры, enrich, pipeline)."""

from typing import Any, Protocol

from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.price_source import FilePricesSource
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.base_parser.markup_policy import MarkupPolicy, make_markup_policy
from parsers.base_parser.parse_statistic import ParserStats, ParseResultStatistic
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.protocols import FileReaderProtocol, RowProcessorProtocol, TitleFilterProtocol
from parsers.base_parser.row_pipeline import make_row_pipeline
from parsers.base_parser.row_processor import RowProcessor
from parsers.base_parser.tire_and_disk_handler import TireAndDiskHandler


class Parser(Protocol):
    """parser protocol"""

    @classmethod
    def supplier_folder_name(cls) -> str: ...

    def get_parsed_items(self) -> list[RowItem]: ...

    def parse(self) -> TireAndDiskResult: ...


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
        group_handler: TireAndDiskHandler | None = None,
    ) -> None:
        self.parsed_items: list[RowItem] = []
        self._package = TireAndDiskResult()
        self.settings = group_handler.settings if group_handler else ParserSettings(parse_config)
        self._logger = LoggerParseProcess(f'{self!r} [tire_and_disk]')
        self.stats = group_handler.stats if group_handler else ParserStats()
        self.price_files = PriceFiles(
            self.settings.parser_params(),
            file_reader or _default_file_reader(self.settings, data_reader),
            self.settings.parse_config().routing,
        )
        self.group_handler = group_handler or TireAndDiskHandler(
            settings=self.settings,
            stats=self.stats,
            pipeline=make_row_pipeline(
                self.settings, self.stats, row_processor=row_processor, title_filter=title_filter
            ),
        )

    def __repr__(self) -> str:
        """Название поставщика из конфига; имя класса (BaseParser) не показываем."""
        return self.settings.title()

    @property
    def product_group(self) -> ProductGroup:
        """Группа определяет модель обработчика и контекст диагностики."""
        return self.group_handler.product_group

    def parse(self) -> TireAndDiskResult:
        if not self.settings.is_active:
            self._logger.log_disable_status()
            return TireAndDiskResult()
        self.price_files.resolve()
        self._logger.log_start()
        self.process()
        self._logger.log_finish(ParseResultStatistic(self.get_parsed_items()))
        return self._package

    def get_parsed_items(self) -> list[RowItem]:
        return self.parsed_items

    def process(self) -> int:
        """Прочитать файлы, отобразить позиции и передать их обработчику группы."""
        files = self.price_files.files or []
        self._logger.log_list_files(files)
        mapped = self.price_files.read_positions(files, self.group_handler.create_position)
        raw_count = len(mapped)
        self.parsed_items += mapped
        self._package = self.group_handler.process(self.parsed_items)
        self.parsed_items = list(self._package.positions)
        return raw_count


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
