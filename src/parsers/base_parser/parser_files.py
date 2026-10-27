"""Чтение прайсов BaseParser: файлы, сырые строки, маппинг в RowItem (делегирует FileReader)."""

from typing import Any

from domain.exceptions import SupplierNotHavePricesError
from domain.row_item.row_item import RowItem
from parsers.base_parser.parser_core import ParserCore
from parsers.xls_reader import IXlsReader


def type_production_from_filename(price_file: str) -> str:
    """Последний суффикс имени файла после `_` (например disks.xls)."""
    return price_file.rpartition('_')[2]


class ParserFiles(ParserCore):
    """Чтение файлов прайса и маппинг строк."""

    def read_rows(self, paths: list[str]) -> list[dict[str, Any]]:
        raw_rows: list[dict[str, Any]] = []
        for price_file in paths:
            self.type_production = type_production_from_filename(price_file)
            raw_rows.extend(self.raw_parse(price_file))
        return raw_rows

    def map_items(self, raw_rows: list[dict[str, Any]]) -> list[RowItem]:
        return [self.settings.parser_params().row_item_adaptor(row_item) for row_item in raw_rows]

    def raw_parse(self, full_file_xls_path: str) -> list[dict[str, Any]]:
        return self._file_reader_impl.raw_parse(full_file_xls_path, self.settings.parser_params())

    def get_data_reader(self, full_file_xls_path: str) -> IXlsReader:
        return self._file_reader_impl.get_data_reader(full_file_xls_path, self.settings.parser_params())

    def get_parsed_items(self) -> list[RowItem]:
        return self.parsed_items

    def _price_files(self) -> list[str]:
        if self.files:
            return self.files
        files = self._file_reader_impl.price_files(self.settings.parser_params())
        if not files:
            supplier_name = self.settings.parser_params().supplier.name
            raise SupplierNotHavePricesError(f'Прайсов у поставщика ({supplier_name}) не обнаружено!')
        return files
