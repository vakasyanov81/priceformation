"""PriceFiles: файлы прайса, чтение строк, маппинг — без BaseParser."""

from unittest.mock import MagicMock

import pytest

from domain.exceptions import SupplierNotHavePricesError
from domain.row_item.row_item import RowItem
from parsers.base_parser.price_files import PriceFiles

_SUPPLIER_NAME = 'Поставщик'
_FOUND = ['found_tires.xls']
_GIVEN = ['given_disks.xls']


def _price_files(found: list[str] | None = None) -> tuple[PriceFiles, MagicMock]:
    settings = MagicMock()
    settings.parser_params.return_value.supplier.name = _SUPPLIER_NAME
    settings.parser_params.return_value.row_item_adaptor = RowItem
    reader = MagicMock()
    reader.price_files.return_value = found or []
    return PriceFiles(settings, reader), reader


def test_resolve_finds_files_in_supplier_folder() -> None:
    price_files, _reader = _price_files(_FOUND)

    assert price_files.resolve() == _FOUND
    assert price_files.files == _FOUND


def test_resolve_keeps_given_files() -> None:
    price_files, reader = _price_files(_FOUND)
    price_files.files = _GIVEN

    assert price_files.resolve() == _GIVEN
    reader.price_files.assert_not_called()


def test_resolve_without_prices_raises_with_supplier_name() -> None:
    price_files, _reader = _price_files([])

    with pytest.raises(SupplierNotHavePricesError, match=_SUPPLIER_NAME):
        price_files.resolve()


def test_read_rows_collects_rows_from_all_files() -> None:
    price_files, reader = _price_files()
    reader.raw_parse.side_effect = [[{'title': 'a'}], [{'title': 'b'}]]

    rows = price_files.read_rows(['x_tires.xls', 'x_disks.xls'])

    assert rows == [{'title': 'a'}, {'title': 'b'}]


def test_map_items_builds_row_items_with_adaptor() -> None:
    price_files, _reader = _price_files()

    mapped = price_files.map_items([{'title': 'a'}])

    assert [row.identity.title for row in mapped] == ['a']
