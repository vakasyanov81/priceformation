"""Источники прайсов поставщика: проверка файлов и распаковка zip-архивов во временную папку."""

import shutil
import tempfile
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from pathlib import Path

from parsers.supplier_price.archive import ZIP_EXTENSION, unzip
from parsers.supplier_price.errors import InvalidPriceExtensionError, SupplierPriceFileNotFoundError

type PriceSources = str | Sequence[str]

_EXCEL_EXTENSIONS = frozenset(('.xls', '.xlsx'))
_ALLOWED_EXTENSIONS = _EXCEL_EXTENSIONS | {'.json'}
_MSG_EXTENSION = 'Недопустимое расширение {0!r} у файла {1}. Допустимые: xls, xlsx, json, zip'
_MSG_NOT_FOUND = 'Файл не найден: {0}'


@contextmanager
def unpacked_dir() -> Generator[Path]:
    """Временная папка для содержимого архивов; удаляется после загрузки."""
    folder = Path(tempfile.mkdtemp(prefix='supplier_prices_'))
    try:
        yield folder
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def expand_sources(sources: PriceSources, unpack_dir: Path) -> list[Path]:
    """Проверить файлы и заменить zip-архивы их содержимым."""
    expanded = [price_path for path in _as_paths(sources) for price_path in _expand(path, unpack_dir)]
    for price_path in expanded:
        _check_extension(price_path)
    return expanded


def is_excel(name: str) -> bool:
    """Расширение xls или xlsx (без учёта регистра)."""
    return Path(name).suffix.lower() in _EXCEL_EXTENSIONS


def _as_paths(sources: PriceSources) -> list[Path]:
    if isinstance(sources, str):
        return [Path(sources)]
    return [Path(source) for source in sources]


def _expand(path: Path, unpack_dir: Path) -> list[Path]:
    if not path.is_file():
        raise SupplierPriceFileNotFoundError(_MSG_NOT_FOUND.format(path))
    if path.suffix.lower() == ZIP_EXTENSION:
        return unzip(path, unpack_dir)
    return [path]


def _check_extension(path: Path) -> None:
    if path.suffix.lower() not in _ALLOWED_EXTENSIONS:
        raise InvalidPriceExtensionError(_MSG_EXTENSION.format(path.suffix, path.name))
