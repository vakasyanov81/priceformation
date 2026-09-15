"""Чтение файлов прайсов и маппинг строк."""

from typing import Any

from parsers.base_parser.price_source import FilePricesSource, PriceSource
from parsers.xls_reader import IXlsReader, XlsReader


class FileReader:
    """Читает xls/json файлы прайсов по данным parser_params."""

    def __init__(
        self,
        *,
        data_reader: type[Any] | None = None,
        price_source: PriceSource | None = None,
    ) -> None:
        self._data_reader = data_reader or XlsReader
        self._price_source = price_source or FilePricesSource()

    def raw_parse(self, path: str, parser_params: Any) -> list[dict[str, Any]]:
        reader = self.get_data_reader(path, parser_params)
        return reader.parse(parser_params.sheet_indexes)

    def get_data_reader(self, path: str, parser_params: Any) -> IXlsReader:
        return self._data_reader.get_instance(
            path,
            {
                'start_row': parser_params.start_row - 1,
                'columns': parser_params.columns,
            },
        )

    def price_files(self, parser_params: Any) -> list[str]:
        return self._price_source.list_files(
            parser_params.supplier.folder_name,
            parser_params.file_templates,
        )
