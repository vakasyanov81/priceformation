"""Correction map for vendor nomenclature titles."""

import traceback
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from python_calamine import CalamineError, CalamineWorkbook, WorksheetNotFound, ZipError

from core.exceptions import CoreExceptionError
from core.log_message import err_msg
from core.parse_paths import get_parse_paths

VENDOR_TITLE_IDX = 0
CORRECT_TITLE_IDX = 1
_NOMENCLATURE_FILE = 'correct-nomenclature.xlsx'


class _NomenclatureCache:
    """Module-level cache for corrected titles."""

    titles: dict[str, str] | None = None


def clear_nomenclature_cache() -> None:
    """Drop the process-level title correction cache."""
    _NomenclatureCache.titles = None


def get_nomenclature_corrected_title(nomenclature_title: str) -> str:
    """Return corrected title from cache or original title."""
    if _NomenclatureCache.titles is None:
        _NomenclatureCache.titles = load_file()

    return _NomenclatureCache.titles.get(nomenclature_title) or nomenclature_title


def load_file() -> dict[str, str]:
    """Load title corrections from correct-nomenclature.xlsx."""
    file_path = get_parse_paths().config_file(_NOMENCLATURE_FILE)
    if not Path(file_path).exists():
        return {}
    return _read_corrections(file_path)


class NomenclatureCorrectionFileError(CoreExceptionError):
    """Ошибка чтения correct-nomenclature.xlsx — файл повреждён или имеет неверную структуру."""


_CORRECTION_ERROR_MSG = (
    'Файл correct-nomenclature.xlsx повреждён или имеет неверную структуру. '
    'Проверьте, что файл — это xlsx с одним листом "Sheet1" и двумя колонками: '
    'исходный заголовок и исправленный заголовок.'
)


def _read_corrections(file_path: str) -> dict[str, str]:
    """Прочитать Sheet1 в словарь vendor_title -> correct_title."""
    try:
        wb = CalamineWorkbook.from_path(file_path)
    except (CalamineError, ZipError) as exc:
        err_msg(f'{_CORRECTION_ERROR_MSG}\nПуть: {file_path}\n{exc!r}\n{traceback.format_exc()}')
        raise NomenclatureCorrectionFileError(_CORRECTION_ERROR_MSG) from exc

    try:
        sheet = wb.get_sheet_by_name('Sheet1')
    except WorksheetNotFound as exc:
        err_msg(
            f'{_CORRECTION_ERROR_MSG}\nПуть: {file_path}\n{exc!r}\n'
            f'Доступные листы: {wb.sheet_names}\n{traceback.format_exc()}',
        )
        raise NomenclatureCorrectionFileError(_CORRECTION_ERROR_MSG) from exc

    rows = sheet.to_python()

    try:
        return dict(_iter_correction_pairs(rows))
    except (IndexError, TypeError) as exc:
        err_msg(
            f'{_CORRECTION_ERROR_MSG}\nПуть: {file_path}\n{exc!r}\n'
            f'Строк в листе: {len(rows)}\n{traceback.format_exc()}',
        )
        raise NomenclatureCorrectionFileError(_CORRECTION_ERROR_MSG) from exc


def _iter_correction_pairs(rows: list[list[Any]]) -> Iterator[tuple[str, str]]:
    """Пары из строк xlsx без заголовка."""
    for row_data in rows[1:]:
        vendor_title = str(row_data[VENDOR_TITLE_IDX])
        correct_title = str(row_data[CORRECT_TITLE_IDX])
        if vendor_title and correct_title:
            yield vendor_title, correct_title
