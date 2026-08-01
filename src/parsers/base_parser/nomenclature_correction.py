"""Correction map for vendor nomenclature titles."""

import os
from pathlib import Path

from python_calamine import CalamineWorkbook

from cfg.main import MainConfig

VENDOR_TITLE_IDX = 0
CORRECT_TITLE_IDX = 1


def get_nomenclature_corrected_title(nomenclature_title: str) -> str:
    """Return corrected title from cache or original title."""
    if getattr(get_nomenclature_corrected_title, "corrected_nomenclatures_", None) is None:
        get_nomenclature_corrected_title.corrected_nomenclatures_ = load_file()

    return (
        getattr(get_nomenclature_corrected_title, "corrected_nomenclatures_", {}).get(nomenclature_title)
        or nomenclature_title
    )


def load_file() -> dict[str, str]:
    """Load title corrections from correct-nomenclature.xlsx."""
    file_path = f"{MainConfig().user_config_folder_path}{os.sep}correct-nomenclature.xlsx"
    if not Path(file_path).exists():
        return {}
    return _read_corrections(file_path)


def _read_corrections(file_path: str) -> dict[str, str]:
    """Прочитать Sheet1 в словарь vendor_title -> correct_title."""
    rows = CalamineWorkbook.from_path(file_path).get_sheet_by_name("Sheet1").to_python()
    return dict(_iter_correction_pairs(rows))


def _iter_correction_pairs(rows):
    """Пары из строк xlsx без заголовка."""
    for row_data in rows[1:]:
        vendor_title = str(row_data[VENDOR_TITLE_IDX])
        correct_title = str(row_data[CORRECT_TITLE_IDX])
        if vendor_title and correct_title:
            yield vendor_title, correct_title
