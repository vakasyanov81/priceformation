"""Настройки парсера: конфиг, параметры, имя поставщика, признак активности."""

from parsers.base_parser.base_parser_config import ParseConfigNotSetError, ParseConfiguration, ParserParams
from parsers.base_parser.manufacturer_finder import ManufacturerFinder


class ParserSettings:
    """Доступ к `ParseConfiguration` и производным от него объектам (кэш поиска производителя)."""

    def __init__(self, parse_config: ParseConfiguration | None = None) -> None:
        self._parse_config = parse_config
        self._manufacturer_finder: ManufacturerFinder | None = None

    def parse_config(self) -> ParseConfiguration:
        if self._parse_config is None:
            raise ParseConfigNotSetError()
        return self._parse_config

    def parser_params(self) -> ParserParams:
        return self.parse_config().parser_params

    def manufacturer_finder(self) -> ManufacturerFinder:
        if self._manufacturer_finder is None:
            aliases = self.parse_config().manufacturer_aliases()
            self._manufacturer_finder = ManufacturerFinder(aliases)
        return self._manufacturer_finder

    @property
    def is_active(self) -> bool:
        return self.parse_config().is_enabled

    def title(self) -> str:
        """Название поставщика из конфига (с листом, если задан)."""
        supplier_name = self.parser_params().supplier.name
        sheet_info = self.parser_params().sheet_info
        if sheet_info:
            return f'{supplier_name} ({sheet_info})'
        return supplier_name
