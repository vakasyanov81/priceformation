"""tests for FilePricesSource and parser price_source injection"""

import re
from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock

import pytest

from cfg import init_cfg
from core.exceptions import SupplierNotHavePricesError
from core.parse_paths import ParsePaths, configure_parse_paths
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.price_source import FilePricesSource, PriceSource

_SUPPLIER = "poshk"
_SUPPLIER_NAME = "Пошк"
_TEMPLATE = "price*"
_XLS_TEMPLATE = "price*.xls"
_XLSX_TEMPLATE = "price*.xlsx"
_PRICE_NAME = "price.xlsx"
_XLS_NAME = "price.xls"
_MISSING_MSG = f"Прайсов у поставщика ({_SUPPLIER_NAME}) не обнаружено!"
_SOURCE_FILE = "file_prices/poshk/price.xlsx"
_GIVEN_FILE = "file_prices/poshk/given.xls"


@pytest.fixture
def _restore_parse_paths() -> Iterator[None]:
    yield
    init_cfg()


class _ListSource:
    def __init__(self, files: list[str]) -> None:
        self.files = files
        self.called = False
        self.folder_name = ""
        self.templates: list[str] = []

    def list_files(self, folder_name: str, templates: list[str]) -> list[str]:
        self.called = True
        self.folder_name = folder_name
        self.templates = templates
        return self.files


class _SilentParser(BaseParser):
    """parse() без чтения xls: только resolve файлов."""

    def __init__(
        self,
        price_source: PriceSource,
        file_prices: list[str] | None = None,
    ) -> None:
        self._parse_params = MagicMock()
        self._parse_params.supplier.folder_name = _SUPPLIER
        self._parse_params.supplier.name = _SUPPLIER_NAME
        self._parse_params.file_templates = [_TEMPLATE]
        super().__init__(file_prices=file_prices, price_source=price_source)

    @property
    def is_active(self) -> bool:
        return True

    def parser_params(self) -> Any:
        return self._parse_params

    def process(self) -> int:
        return 0

    def after_process(self) -> None:
        """Skip percent markup in file-source tests."""


def _configure_prices(tmp_path: Any, prices_root: Any) -> None:
    configure_parse_paths(
        ParsePaths(file_prices_folder=str(prices_root), user_config_folder=str(tmp_path)),
    )


def test_file_prices_source_uses_parse_paths(tmp_path: Any, _restore_parse_paths: None) -> None:
    """список прайсов берётся из file_prices_folder, не из cfg."""
    prices_root = tmp_path / "file_prices"
    supplier_dir = prices_root / _SUPPLIER
    supplier_dir.mkdir(parents=True)
    price_file = supplier_dir / _PRICE_NAME
    price_file.write_bytes(b"x")
    _configure_prices(tmp_path, prices_root)
    files = FilePricesSource().list_files(_SUPPLIER, [_TEMPLATE])
    assert str(price_file) in files


def test_file_prices_source_keeps_template_order(tmp_path: Any, _restore_parse_paths: None) -> None:
    """файлы идут в порядке шаблонов, как list.extend(glob)."""
    prices_root = tmp_path / "file_prices"
    supplier_dir = prices_root / _SUPPLIER
    supplier_dir.mkdir(parents=True)
    xls_file = supplier_dir / _XLS_NAME
    xlsx_file = supplier_dir / _PRICE_NAME
    xls_file.write_bytes(b"x")
    xlsx_file.write_bytes(b"x")
    _configure_prices(tmp_path, prices_root)
    files = FilePricesSource().list_files(_SUPPLIER, [_XLS_TEMPLATE, _XLSX_TEMPLATE])
    assert files == [str(xls_file), str(xlsx_file)]


def test_file_prices_source_empty_is_empty_list(tmp_path: Any, _restore_parse_paths: None) -> None:
    """нет файлов — пустой список, без исключения."""
    prices_root = tmp_path / "file_prices"
    (prices_root / _SUPPLIER).mkdir(parents=True)
    _configure_prices(tmp_path, prices_root)
    assert FilePricesSource().list_files(_SUPPLIER, [_TEMPLATE]) == []


def test_parser_uses_price_source() -> None:
    source = _ListSource([_SOURCE_FILE])
    parser = _SilentParser(source)
    parser.parse()
    assert source.folder_name == _SUPPLIER
    assert source.templates == [_TEMPLATE]
    assert parser.files == [_SOURCE_FILE]


def test_parser_skips_source_if_files_set() -> None:
    source = _ListSource([_SOURCE_FILE])
    parser = _SilentParser(source, file_prices=[_GIVEN_FILE])
    parser.parse()
    assert not source.called
    assert parser.files == [_GIVEN_FILE]


def test_parser_missing_prices_raises() -> None:
    parser = _SilentParser(_ListSource([]))
    with pytest.raises(SupplierNotHavePricesError, match=re.escape(_MISSING_MSG)):
        parser.parse()
