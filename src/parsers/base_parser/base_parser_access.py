"""Config, vendor status and manufacturer finder for a parser instance."""

from parsers import data_provider
from parsers.base_parser.base_parser_config import ParseConfiguration, ParserParams
from parsers.base_parser.manufacturer_finder import ManufacturerFinder


class ParseConfigNotSetError(RuntimeError):
    """Raised when parse_config() is used before config is assigned."""

    def __init__(self) -> None:
        super().__init__("parse_config is not set")


class ParserConfigAccess:
    _parse_config: ParseConfiguration | None
    _black_list: list[str] | None
    _stop_words: list[str] | None
    _manufacturer_finder: ManufacturerFinder | None

    def parse_config(self) -> ParseConfiguration:
        if self._parse_config is None:
            raise ParseConfigNotSetError()
        return self._parse_config

    def set_parse_config(self, parse_config: ParseConfiguration) -> None:
        self._parse_config = parse_config
        self._black_list = None
        self._stop_words = None
        self._manufacturer_finder = None

    def parser_params(self) -> ParserParams:
        return self.parse_config().parser_params

    def manufacturer_finder(self) -> ManufacturerFinder:
        if self._manufacturer_finder is None:
            aliases = self.parse_config().manufacturer_aliases()
            self._manufacturer_finder = ManufacturerFinder(aliases)
        return self._manufacturer_finder

    def get_current_vendor_config(self) -> data_provider.VendorParams:
        """get vendor configuration"""
        folder_name = self.parser_params().supplier.folder_name
        vendor = self.parse_config().all_vendor_config().get(folder_name)
        return vendor or data_provider.VendorParams(enabled=0)

    @property
    def is_active(self) -> bool:
        return bool(self.get_current_vendor_config().enabled)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        supplier_name = self.parser_params().supplier.name
        sup_name = f"{class_name}: {supplier_name}"
        sheet_info = self.parser_params().sheet_info
        if sheet_info:
            sup_name = f"{sup_name} ({sheet_info})"
        return sup_name
