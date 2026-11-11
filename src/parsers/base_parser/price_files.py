"""Прайс-файлы поставщика: список файлов, чтение строк и маппинг через фабрику модели."""

from collections.abc import Callable
from typing import Any

from domain.exceptions import SupplierNotHavePricesError
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.protocols import FileReaderProtocol
from parsers.xls_reader import IXlsReader

type RawFields = dict[str, Any]
type PositionFactory[TPosition] = Callable[[RawFields], TPosition]


class PriceFiles:
    """Файлы прайса и их разбор; параметры берёт из `ParserSettings`, чтение — из `FileReaderProtocol`."""

    def __init__(self, settings: ParserSettings, file_reader: FileReaderProtocol) -> None:
        self.settings = settings
        self.file_reader = file_reader
        self.files: list[str] | None = None

    def resolve(self) -> list[str]:
        """Файлы для разбора: заданные явно или найденные в папке поставщика."""
        if not self.files:
            self.files = self._find_files()
        return self.files

    def read_rows(self, paths: list[str]) -> list[RawFields]:
        raw_rows: list[RawFields] = []
        for price_file in paths:
            raw_rows.extend(self.raw_parse(price_file))
        return raw_rows

    def map_items[TPosition](
        self, raw_rows: list[RawFields], position_factory: PositionFactory[TPosition]
    ) -> list[TPosition]:
        return [position_factory(row_item) for row_item in raw_rows]

    def raw_parse(self, full_file_xls_path: str) -> list[RawFields]:
        return self.file_reader.raw_parse(full_file_xls_path, self.settings.parser_params())

    def get_data_reader(self, full_file_xls_path: str) -> IXlsReader:
        return self.file_reader.get_data_reader(full_file_xls_path, self.settings.parser_params())

    def _find_files(self) -> list[str]:
        files = self.file_reader.price_files(self.settings.parser_params())
        if not files:
            supplier_name = self.settings.parser_params().supplier.name
            raise SupplierNotHavePricesError(f'Прайсов у поставщика ({supplier_name}) не обнаружено!')
        return files
