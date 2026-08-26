"""Read price files and map raw rows to RowItem."""

from typing import Any, Protocol

from core.exceptions import SupplierNotHavePricesError
from parsers.base_parser.base_parser_hooks import ParserRowHooks
from parsers.base_parser.price_source import PriceSource
from parsers.row_item.row_item import RowItem
from parsers.xls_reader import IXlsReader


class ReaderFactory(Protocol):
    """Класс-ридер с фабричным get_instance (XlsReader / JsonPriceReader / Fake*)."""

    @classmethod
    def get_instance(cls, file_path: str, *args: Any, **kwargs: Any) -> IXlsReader: ...


class ParserFileReader(ParserRowHooks):
    data_reader: type[ReaderFactory]
    files: list[str] | None
    _price_source: PriceSource
    type_production: str | None
    parsed_items: list[RowItem]

    def read_rows(self, paths: list[str]) -> list[dict[str, Any]]:
        raw_rows: list[dict[str, Any]] = []
        for price_file in paths:
            self.type_production = _type_production_from_filename(price_file)
            raw_rows.extend(self.raw_parse(price_file))
        return raw_rows

    def map_items(self, raw_rows: list[dict[str, Any]]) -> list[RowItem]:
        return [self.parser_params().row_item_adaptor(row_item) for row_item in raw_rows]

    def raw_parse(self, full_file_xls_path: str) -> list[dict[str, Any]]:
        reader = self.get_data_reader(full_file_xls_path)
        return reader.parse(self.parser_params().sheet_indexes)

    def get_data_reader(self, full_file_xls_path: str) -> IXlsReader:
        return self.data_reader.get_instance(
            full_file_xls_path,
            {
                "start_row": self.parser_params().start_row - 1,
                "columns": self.parser_params().columns,
            },
        )

    def get_parsed_items(self) -> list[RowItem]:
        return self.parsed_items

    def _price_files(self) -> list[str]:
        if self.files:
            return self.files
        parse_params = self.parser_params()
        files = self._price_source.list_files(
            parse_params.supplier.folder_name,
            parse_params.file_templates,
        )
        if not files:
            supplier_name = parse_params.supplier.name
            raise SupplierNotHavePricesError(f"Прайсов у поставщика ({supplier_name}) не обнаружено!")
        return files


def _type_production_from_filename(price_file: str) -> str:
    """Последний суффикс имени файла после `_` (например disks.xls)."""
    return price_file.rsplit("_", maxsplit=1)[-1]
