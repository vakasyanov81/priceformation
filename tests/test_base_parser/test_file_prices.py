"""tests for get_file_prices via ParsePaths"""

from typing import Any, Iterator
from unittest.mock import MagicMock

import pytest

from cfg import init_cfg
from core.exceptions import SupplierNotHavePricesError
from core.parse_paths import ParsePaths, configure_parse_paths
from parsers.base_parser.base_parser import get_file_prices

_SUPPLIER = "poshk"
_TEMPLATE = "price*"
_PRICE_NAME = "price.xlsx"


@pytest.fixture
def _restore_parse_paths() -> Iterator[None]:
    yield
    init_cfg()


def _parser(folder_name: str = _SUPPLIER) -> MagicMock:
    parser = MagicMock()
    parser_params = parser.parser_params.return_value
    parser_params.supplier.folder_name = folder_name
    parser_params.supplier.name = "Пошк"
    parser_params.file_templates = [_TEMPLATE]
    return parser


def test_get_file_prices_uses_parse_paths(tmp_path: Any, _restore_parse_paths: None) -> None:
    """список прайсов берётся из file_prices_folder, не из cfg."""
    prices_root = tmp_path / "file_prices"
    supplier_dir = prices_root / _SUPPLIER
    supplier_dir.mkdir(parents=True)
    price_file = supplier_dir / _PRICE_NAME
    price_file.write_bytes(b"x")
    configure_parse_paths(
        ParsePaths(file_prices_folder=str(prices_root), user_config_folder=str(tmp_path)),
    )
    files = get_file_prices(_parser())
    assert str(price_file) in files


def test_get_file_prices_missing_raises(tmp_path: Any, _restore_parse_paths: None) -> None:
    """нет файлов — SupplierNotHavePricesError."""
    prices_root = tmp_path / "file_prices"
    (prices_root / _SUPPLIER).mkdir(parents=True)
    configure_parse_paths(
        ParsePaths(file_prices_folder=str(prices_root), user_config_folder=str(tmp_path)),
    )
    with pytest.raises(SupplierNotHavePricesError):
        get_file_prices(_parser())
