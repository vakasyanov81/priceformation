"""Источник файлов прайса: glob по каталогу поставщика, без cfg."""

from pathlib import Path
from typing import Protocol

from core.config_provider import get_config_provider


class PriceSource(Protocol):
    """Список путей прайсов для папки поставщика и glob-шаблонов."""

    def list_files(self, folder_name: str, templates: list[str]) -> list[str]:
        """Пути файлов в порядке шаблонов; внутри шаблона — порядок pathlib."""
        ...


class FilePricesSource:
    """Прайсы на диске: glob шаблонов в file_prices/<folder_name>/."""

    def list_files(self, folder_name: str, templates: list[str]) -> list[str]:
        supplier_folder = Path(get_config_provider().price_folder(folder_name))
        return _glob_price_files(supplier_folder, templates)


def _glob_price_files(supplier_folder: Path, templates: list[str]) -> list[str]:
    """Собрать пути прайсов по glob-шаблонам."""
    found: list[str] = []
    for template in templates:
        found.extend(str(path) for path in supplier_folder.glob(template))
    return found
