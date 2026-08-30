"""Загрузка прайсов поставщиков в file_prices."""

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from core.parse_paths import ParsePaths, _CurrentParsePaths, configure_parse_paths
from parsers.load_supplier_prices import load_supplier_prices, parse_prices_json
from parsers.supplier_price_errors import (
    InvalidPriceExtensionError,
    SupplierPriceFileNotFoundError,
    SupplierPricesMappingError,
    UnknownSupplierCodeError,
)

_CATALOG = {
    "1": {"sup_code": "poshk", "sup_title": "Пошк"},
    "3": {"sup_code": "pioner", "sup_title": "Пионер"},
}
_CATALOG_PATCH = "parsers.load_supplier_prices.all_vendor_supplier_catalog"
_XLS_BYTES = b"xls-content"
_XLSX_BYTES = b"xlsx-content"


@pytest.fixture
def _restore_parse_paths() -> Iterator[None]:
    previous = _CurrentParsePaths.configured  # noqa: WPS437
    yield
    _CurrentParsePaths.configured = previous  # noqa: WPS437


@pytest.fixture
def prices_root(tmp_path: Path, _restore_parse_paths: None) -> Path:
    file_prices = tmp_path / "file_prices"
    file_prices.mkdir()
    configure_parse_paths(
        ParsePaths(
            file_prices_folder=str(file_prices),
            user_config_folder=str(tmp_path / "cfg"),
            result_folder=str(file_prices / "result"),
        ),
    )
    return file_prices


def _write_source(tmp_path: Path, name: str, file_bytes: bytes) -> Path:
    source = tmp_path / "incoming" / name
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(file_bytes)
    return source


def test_parse_prices_json_object() -> None:
    """валидный JSON-объект строк."""
    assert parse_prices_json('{"1": "/incoming/a.xls"}') == {"1": "/incoming/a.xls"}


def test_parse_prices_json_invalid() -> None:
    """не JSON."""
    with pytest.raises(SupplierPricesMappingError):
        parse_prices_json("not-json")


def test_parse_prices_json_not_object() -> None:
    """не объект."""
    with pytest.raises(SupplierPricesMappingError, match="Ожидается объект"):
        parse_prices_json('["1"]')


def test_parse_prices_json_empty_value() -> None:
    """пустой путь."""
    with pytest.raises(SupplierPricesMappingError, match="непустыми"):
        parse_prices_json('{"1": ""}')


def test_parse_prices_json_non_string_value() -> None:
    """путь не строка."""
    with pytest.raises(SupplierPricesMappingError, match="непустыми"):
        parse_prices_json('{"1": 1}')


def test_load_moves_and_renames(tmp_path: Path, prices_root: Path) -> None:
    """файл перемещается в папку поставщика как price.xls."""
    source = _write_source(tmp_path, "any_price_name.xls", _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dests = load_supplier_prices({"1": str(source)})
    dest = prices_root / "poshk" / "price.xls"
    assert dests == [str(dest)]
    assert dest.read_bytes() == _XLS_BYTES
    assert not source.exists()


def test_load_xlsx_keeps_extension(tmp_path: Path, prices_root: Path) -> None:
    """xlsx сохраняет расширение."""
    source = _write_source(tmp_path, "any.xlsx", _XLSX_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        load_supplier_prices({"1": str(source)})
    dest = prices_root / "poshk" / "price.xlsx"
    assert dest.read_bytes() == _XLSX_BYTES
    assert not source.exists()


def test_load_uppercase_extension(tmp_path: Path, prices_root: Path) -> None:
    """XLS → price.xls."""
    source = _write_source(tmp_path, "any.XLS", _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        load_supplier_prices({"1": str(source)})
    assert (prices_root / "poshk" / "price.xls").is_file()


def test_load_creates_supplier_folder(tmp_path: Path, prices_root: Path) -> None:
    """папка поставщика создаётся."""
    source = _write_source(tmp_path, "a.xls", _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        load_supplier_prices({"3": str(source)})
    assert (prices_root / "pioner" / "price.xls").is_file()


def test_load_replaces_other_extension(tmp_path: Path, prices_root: Path) -> None:
    """старый price.xls удаляется при загрузке xlsx."""
    dest_dir = prices_root / "poshk"
    dest_dir.mkdir()
    old_xls = dest_dir / "price.xls"
    old_xls.write_bytes(b"old")
    rest = dest_dir / "rest.xls"
    rest.write_bytes(b"rest")
    source = _write_source(tmp_path, "new.xlsx", _XLSX_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        load_supplier_prices({"1": str(source)})
    assert not old_xls.exists()
    assert (dest_dir / "price.xlsx").read_bytes() == _XLSX_BYTES
    assert rest.read_bytes() == b"rest"


def test_load_already_in_place(prices_root: Path) -> None:
    """уже price.xls в папке поставщика — не трогаем."""
    dest_dir = prices_root / "poshk"
    dest_dir.mkdir()
    dest = dest_dir / "price.xls"
    dest.write_bytes(_XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dest_paths = load_supplier_prices({"1": str(dest)})
    assert dest_paths == [str(dest)]
    assert dest.read_bytes() == _XLS_BYTES


def test_load_two_suppliers(tmp_path: Path, prices_root: Path) -> None:
    """несколько поставщиков за один вызов."""
    first = _write_source(tmp_path, "a.xls", _XLS_BYTES)
    second = _write_source(tmp_path, "b.xlsx", _XLSX_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dests = load_supplier_prices({"1": str(first), "3": str(second)})
    assert dests == [
        str(prices_root / "poshk" / "price.xls"),
        str(prices_root / "pioner" / "price.xlsx"),
    ]


def test_load_rejects_extension(tmp_path: Path, prices_root: Path) -> None:
    """csv нельзя."""
    source = _write_source(tmp_path, "a.csv", b"csv")
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(InvalidPriceExtensionError, match="csv"):
        load_supplier_prices({"1": str(source)})
    assert source.exists()


def test_load_rejects_json(tmp_path: Path, prices_root: Path) -> None:
    """json нельзя."""
    source = _write_source(tmp_path, "a.json", b"{}")
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(InvalidPriceExtensionError):
        load_supplier_prices({"1": str(source)})


def test_load_missing_file(tmp_path: Path, prices_root: Path) -> None:
    """нет файла."""
    missing = tmp_path / "incoming" / "gone.xls"
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(SupplierPriceFileNotFoundError):
        load_supplier_prices({"1": str(missing)})


def test_load_unknown_supplier(tmp_path: Path, prices_root: Path) -> None:
    """неизвестный ИД — до проверки файла."""
    source = _write_source(tmp_path, "a.xls", _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(UnknownSupplierCodeError, match="99"):
        load_supplier_prices({"99": str(source)})
    assert source.exists()


def test_load_validates_all_before_move(tmp_path: Path, prices_root: Path) -> None:
    """ошибка второго файла — первый не перемещается."""
    good = _write_source(tmp_path, "a.xls", _XLS_BYTES)
    bad = _write_source(tmp_path, "b.csv", b"csv")
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(InvalidPriceExtensionError):
        load_supplier_prices({"1": str(good), "3": str(bad)})
    assert good.exists()
    assert not (prices_root / "poshk" / "price.xls").exists()


def test_load_empty_mapping(prices_root: Path) -> None:
    """пустая карта — пустой список."""
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        assert load_supplier_prices({}) == []
