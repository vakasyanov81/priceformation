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
    parser_params = MagicMock()
    parser_params.supplier.name = _SUPPLIER_NAME
    reader = MagicMock()
    reader.price_files.return_value = found or []
    return PriceFiles(parser_params, reader), reader


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


def test_read_positions_reads_files_and_maps_rows() -> None:
    """Чтение и отображение колонок — одна операция, модель задаёт фабрика."""
    price_files, reader = _price_files()
    reader.raw_parse.side_effect = [[{'title': 'a'}], [{'title': 'b'}]]

    positions = price_files.read_positions(['x_tires.xls', 'x_disks.xls'], RowItem)

    assert [row.identity.title for row in positions] == ['a', 'b']
