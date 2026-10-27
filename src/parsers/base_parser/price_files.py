"""Прайс-файлы поставщика: список файлов, чтение сырых строк, маппинг в RowItem."""

from typing import Any

from domain.exceptions import SupplierNotHavePricesError
from domain.row_item.row_item import RowItem
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.protocols import FileReaderProtocol
from parsers.xls_reader import IXlsReader


def type_production_from_filename(price_file: str) -> str:
    """Последний суффикс имени файла после `_` (например disks.xls)."""
    return price_file.rpartition('_')[2]


class PriceFiles:
    """Файлы прайса и их разбор; параметры берёт из `ParserSettings`, чтение — из `FileReaderProtocol`."""

    def __init__(self, settings: ParserSettings, file_reader: FileReaderProtocol) -> None:
        self.settings = settings
        self.file_reader = file_reader
        self.files: list[str] | None = None
        self.type_production: str | None = None

    def resolve(self) -> list[str]:
        """Файлы для разбора: заданные явно или найденные в папке поставщика."""
        if not self.files:
            self.files = self._find_files()
        return self.files

    def read_rows(self, paths: list[str]) -> list[dict[str, Any]]:
        raw_rows: list[dict[str, Any]] = []
        for price_file in paths:
            self.type_production = type_production_from_filename(price_file)
            raw_rows.extend(self.raw_parse(price_file))
        return raw_rows

    def map_items(self, raw_rows: list[dict[str, Any]]) -> list[RowItem]:
        return [self.settings.parser_params().row_item_adaptor(row_item) for row_item in raw_rows]

    def raw_parse(self, full_file_xls_path: str) -> list[dict[str, Any]]:
        return self.file_reader.raw_parse(full_file_xls_path, self.settings.parser_params())

    def get_data_reader(self, full_file_xls_path: str) -> IXlsReader:
        return self.file_reader.get_data_reader(full_file_xls_path, self.settings.parser_params())

    def _find_files(self) -> list[str]:
        files = self.file_reader.price_files(self.settings.parser_params())
        if not files:
            supplier_name = self.settings.parser_params().supplier.name
            raise SupplierNotHavePricesError(f'Прайсов у поставщика ({supplier_name}) не обнаружено!')
        return files
