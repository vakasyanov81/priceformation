import os
from pathlib import Path

from python_calamine import CalamineWorkbook

from cfg.main import MainConfig


def get_nomenclature_corrected_title(nomenclature_title: str) -> str:
    if getattr(get_nomenclature_corrected_title, "corrected_nomenclatures_", None) is None:
        setattr(get_nomenclature_corrected_title, "corrected_nomenclatures_", load_file())

    return (
        getattr(get_nomenclature_corrected_title, "corrected_nomenclatures_", {}).get(nomenclature_title)
        or nomenclature_title
    )


def load_file() -> dict:
    vendor_nomenclature_title_index = 0
    correct_nomenclature_title_index = 1
    _file = MainConfig().user_config_folder_path + os.sep + "correct-nomenclature.xlsx"
    if not Path(_file).exists():
        return {}

    wb = CalamineWorkbook.from_path(_file)

    data = wb.get_sheet_by_name("Sheet1").to_python()
    result_data = {}

    for i, data_ in enumerate(data):
        # skip header
        if i == 0:
            continue
        vendor_nomenclature_title = data_[vendor_nomenclature_title_index]
        correct_nomenclature_title = data_[correct_nomenclature_title_index]
        if vendor_nomenclature_title and correct_nomenclature_title:
            result_data[vendor_nomenclature_title] = correct_nomenclature_title
    return result_data
