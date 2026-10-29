"""Источник файлов прайса: glob по каталогу поставщика, без cfg."""

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from domain.protocols import ConfigProvider


class PriceSource(Protocol):
    """Список путей прайсов для папки поставщика и glob-шаблонов."""

    def list_files(self, folder_name: str, templates: Sequence[str]) -> list[str]:
        """Пути файлов в порядке шаблонов; внутри шаблона — порядок pathlib."""
        ...


class FilePricesSource:
    """Прайсы на диске: glob шаблонов в file_prices/<folder_name>/."""

    def __init__(self, config_provider: ConfigProvider) -> None:
        self._config_provider = config_provider

    def list_files(self, folder_name: str, templates: Sequence[str]) -> list[str]:
        supplier_folder = Path(self._config_provider.price_folder(folder_name))
        return _glob_price_files(supplier_folder, templates)


def _glob_price_files(supplier_folder: Path, templates: Sequence[str]) -> list[str]:
    """Собрать пути прайсов по glob-шаблонам."""
    found: list[str] = []
    for template in templates:
        found.extend(str(path) for path in supplier_folder.glob(template))
    return found
