"""Распаковка zip-архива с прайсами поставщика во временную папку."""

import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from parsers.supplier_price_errors import InvalidPriceExtensionError, SupplierPriceFileNotFoundError

ZIP_EXTENSION = '.zip'
_MACOS_SERVICE_FOLDER = '__MACOSX/'
_MSG_EMPTY_ZIP = 'В архиве {0} нет файлов'
_MSG_BAD_ZIP = 'Файл {0} не является zip-архивом'


def unzip(archive: Path, unpack_dir: Path) -> list[Path]:
    """Файлы архива без вложенных папок; каждый — в свою подпапку, чтобы одинаковые имена не затёрлись."""
    try:
        with zipfile.ZipFile(archive) as zip_file:
            extracted = _extract_all(zip_file, Path(tempfile.mkdtemp(dir=unpack_dir)))
    except zipfile.BadZipFile as exc:
        raise InvalidPriceExtensionError(_MSG_BAD_ZIP.format(archive.name)) from exc
    if not extracted:
        raise SupplierPriceFileNotFoundError(_MSG_EMPTY_ZIP.format(archive.name))
    return extracted


def _extract_all(zip_file: zipfile.ZipFile, target_root: Path) -> list[Path]:
    members = [member for member in zip_file.infolist() if _is_price_member(member)]
    extracted: list[Path] = []
    for index, member in enumerate(members):
        extracted.append(_extract(zip_file, member, target_root / str(index)))
    return extracted


def _extract(zip_file: zipfile.ZipFile, member: zipfile.ZipInfo, folder: Path) -> Path:
    """Записать файл архива в folder под его именем: путь из архива (`../x`) не используется."""
    folder.mkdir()
    target = folder / PurePosixPath(member.filename).name
    with zip_file.open(member) as packed, target.open('wb') as unpacked:
        shutil.copyfileobj(packed, unpacked)
    return target


def _is_price_member(member: zipfile.ZipInfo) -> bool:
    """Обычный файл архива: не папка, не служебный файл macOS и не скрытый файл."""
    if member.is_dir() or member.filename.startswith(_MACOS_SERVICE_FOLDER):
        return False
    return not PurePosixPath(member.filename).name.startswith('.')
