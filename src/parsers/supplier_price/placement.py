"""Раскладка файлов в папку поставщика: замена одноимённых и устаревших Excel-прайсов."""

import shutil
from dataclasses import dataclass
from pathlib import Path

from domain.protocols import ConfigProvider
from parsers.supplier_file_rules import PriceFile, SupplierFileRules
from parsers.supplier_price.sources import is_excel


@dataclass(frozen=True, slots=True)
class SupplierUpload:
    """Проверенная загрузка одного поставщика: папка, правила имён и файлы с назначенными именами."""

    folder: str
    rules: SupplierFileRules
    files: list[PriceFile]


def place_files(upload: SupplierUpload, config_provider: ConfigProvider) -> list[str]:
    """Положить файлы в папку поставщика; при новых Excel-прайсах удалить прежние."""
    dest_dir = Path(config_provider.price_folder(upload.folder))
    dest_dir.mkdir(parents=True, exist_ok=True)
    if any(is_excel(price_file.name) for price_file in upload.files):
        _remove_stale_excel(upload, dest_dir)
    return [_move_price(price_file.source, dest_dir / price_file.name) for price_file in upload.files]


def _remove_stale_excel(upload: SupplierUpload, dest_dir: Path) -> None:
    incoming = {price_file.source.resolve() for price_file in upload.files}
    for path in dest_dir.iterdir():
        if _is_stale(path, upload.rules, incoming):
            path.unlink()


def _is_stale(path: Path, rules: SupplierFileRules, incoming: set[Path]) -> bool:
    """Прежний Excel-прайс поставщика, который не передан в этой загрузке."""
    if not path.is_file() or not rules.is_excel_price(path.name):
        return False
    return path.resolve() not in incoming


def _move_price(source: Path, dest: Path) -> str:
    if source.resolve() != dest.resolve():
        shutil.move(source, dest)
    return str(dest)
