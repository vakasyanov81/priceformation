"""Загрузка файлов прайсов поставщиков в file_prices."""

import json
import shutil
from collections.abc import Mapping
from pathlib import Path

from core.parse_paths import get_parse_paths
from parsers.all_vendors import all_vendor_supplier_catalog
from parsers.supplier_price_errors import (
    InvalidPriceExtensionError,
    SupplierPriceFileNotFoundError,
    SupplierPricesMappingError,
    UnknownSupplierCodeError,
)

_ALLOWED_EXTENSIONS = frozenset((".xls", ".xlsx"))
_PRICE_STEM = "price"
_MSG_MAPPING = "Ожидается объект {ид_или_код_поставщика: путь_к_файлу}"
_MSG_NONEMPTY = "Ключ поставщика и путь к файлу должны быть непустыми строками"
_MSG_EXTENSION = "Недопустимое расширение {0!r}. Допустимые: xls, xlsx"
_MSG_UNKNOWN = "Неизвестный ИД или код поставщика: {0}"


def parse_prices_json(raw: str) -> dict[str, str]:
    """Разобрать JSON-объект ИД или sup_code → путь к файлу."""
    try:
        loaded: object = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SupplierPricesMappingError(str(exc)) from exc
    if not isinstance(loaded, dict):
        raise SupplierPricesMappingError(_MSG_MAPPING)
    mapping: dict[str, str] = {}
    for key, path in loaded.items():
        if not (isinstance(key, str) and key and isinstance(path, str) and path):
            raise SupplierPricesMappingError(_MSG_NONEMPTY)
        mapping[key] = path
    return mapping


def load_supplier_prices(mapping: Mapping[str, str]) -> list[str]:
    """Переместить файлы в папки поставщиков как price.xls / price.xlsx."""
    catalog = all_vendor_supplier_catalog()
    prepared = [_job_for(key, path, catalog) for key, path in mapping.items()]
    return [_move_price(*job) for job in prepared]


def catalog_entry_for(
    supplier_key: str,
    catalog: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Запись каталога по ИД поставщика или sup_code."""
    by_id = catalog.get(supplier_key)
    if by_id is not None:
        return by_id
    for entry in catalog.values():
        if entry["sup_code"] == supplier_key:
            return entry
    raise UnknownSupplierCodeError(_MSG_UNKNOWN.format(supplier_key))


def _job_for(
    supplier_key: str,
    source_raw: str,
    catalog: dict[str, dict[str, str]],
) -> tuple[Path, Path]:
    source = Path(source_raw)
    dest = _destination(source, catalog_entry_for(supplier_key, catalog)["sup_code"])
    _ensure_xls_file(source)
    return source, dest


def _destination(source: Path, folder: str) -> Path:
    dest_dir = Path(get_parse_paths().file_prices_folder) / folder
    return dest_dir / (_PRICE_STEM + source.suffix.lower())


def _ensure_xls_file(source: Path) -> None:
    if source.suffix.lower() not in _ALLOWED_EXTENSIONS:
        raise InvalidPriceExtensionError(_MSG_EXTENSION.format(source.suffix))
    if not source.is_file():
        raise SupplierPriceFileNotFoundError(f"Файл не найден: {source}")


def _move_price(source: Path, dest: Path) -> str:
    if source.resolve() == dest.resolve():
        return str(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    for extension in _ALLOWED_EXTENSIONS:
        (dest.parent / (_PRICE_STEM + extension)).unlink(missing_ok=True)
    shutil.move(source, dest)
    return str(dest)
