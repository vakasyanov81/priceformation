"""Файловый парсер аккумуляторной секции без шинного pipeline."""

from domain.battery.result import BatteryResult
from domain.product_groups import ProductGroup
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.file_reader import FileReader, data_reader_for
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.price_source import FilePricesSource
from parsers.battery.handler import BatteryHandler


class BatteryParser:
    """Чтение общего маршрута и обработка только аккумуляторных строк."""

    def __init__(self, config: ParseConfiguration, group_handler: BatteryHandler) -> None:
        self.settings = ParserSettings(config)
        self.stats = ParserStats()
        self._group_handler = group_handler
        vendor = config.vendor_config
        reader = FileReader(
            data_reader=data_reader_for(vendor.reader if vendor else 'xls'),
            price_source=FilePricesSource(config.config_provider),
        )
        self.price_files = PriceFiles(config.parser_params, reader, config.routing)

    def __repr__(self) -> str:
        return self.settings.title()

    @property
    def product_group(self) -> ProductGroup:
        return self._group_handler.product_group

    def parse(self) -> BatteryResult:
        """Отключённая секция сохраняет пустой пакет и не читает файлы."""
        process_log = LoggerParseProcess(f'{self!r} [batteries]')
        if not self.settings.is_active:
            process_log.log_disable_status()
            return BatteryResult()
        paths = self.price_files.resolve()
        process_log.log_start()
        process_log.log_list_files(paths)
        package = self._group_handler.process_fields(self.price_files.read_rows(paths))
        process_log.log_finish()
        return package
