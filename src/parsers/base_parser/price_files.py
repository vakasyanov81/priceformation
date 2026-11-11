"""Общая механика чтения прайса: файлы поставщика, строки листов и отображение колонок.

Коллаборатор не знает о доменной модели и её стратегиях: он получает параметры
чтения секции и фабрику позиции. Поэтому одно и то же чтение используется
любой товарной группой, а обработка строк остаётся в её обработчике.
"""

from collections.abc import Callable
from typing import Any

from domain.exceptions import SupplierNotHavePricesError
from parsers.base_parser.base_parser_config import ParserParams
from parsers.base_parser.protocols import FileReaderProtocol
from parsers.base_parser.routing import VendorRouting
from parsers.xls_reader import IXlsReader

type RawFields = dict[str, Any]
type PositionFactory[TPosition] = Callable[[RawFields], TPosition]


class PriceFiles:
    """Файлы прайса и их разбор; параметры чтения секции и читатель передаются извне."""

    def __init__(
        self, parser_params: ParserParams, file_reader: FileReaderProtocol, routing: VendorRouting | None = None
    ) -> None:
        self.parser_params = parser_params
        self.file_reader = file_reader
        self.routing = routing
        self.files: list[str] | None = None

    def resolve(self) -> list[str]:
        """Файлы для разбора: заданные явно или найденные в папке поставщика."""
        if self.routing:
            section_id = self.parser_params.supplier.code
            self.files = self.routing.resolve(section_id, self.file_reader, self.files)
        elif not self.files:
            self.files = self._find_files()
        return self.files

    def read_rows(self, paths: list[str]) -> list[RawFields]:
        if self.routing:
            return self.routing.read_rows(self.parser_params.supplier.code)
        raw_rows: list[RawFields] = []
        for price_file in paths:
            raw_rows.extend(self.raw_parse(price_file))
        return raw_rows

    def read_positions[TPosition](
        self, paths: list[str], position_factory: PositionFactory[TPosition]
    ) -> list[TPosition]:
        """Прочитать строки всех файлов и отобразить их в позиции модели."""
        return [position_factory(row_item) for row_item in self.read_rows(paths)]

    def raw_parse(self, full_file_xls_path: str) -> list[RawFields]:
        return self.file_reader.raw_parse(full_file_xls_path, self.parser_params)

    def get_data_reader(self, full_file_xls_path: str) -> IXlsReader:
        return self.file_reader.get_data_reader(full_file_xls_path, self.parser_params)

    def _find_files(self) -> list[str]:
        if self.routing:
            return self.routing.resolve(self.parser_params.supplier.code, self.file_reader)
        files = self.file_reader.price_files(self.parser_params)
        if not files:
            supplier_name = self.parser_params.supplier.name
            raise SupplierNotHavePricesError(f'Прайсов у поставщика ({supplier_name}) не обнаружено!')
        return files
