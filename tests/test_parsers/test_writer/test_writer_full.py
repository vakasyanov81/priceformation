"""tests write price with all parsed fields"""

import datetime
from typing import Any

from parsers.row_item.row_item import RowItem
from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.tmpl.for_full import ForFull
from parsers.writer.xls_writer import XlsWriter

from .fixtures import write_data

_CHARACTERISTIC_FIELDS = (
    RowItem.width.name,
    RowItem.height_percent.name,
    RowItem.diameter.name,
    RowItem.ext_diameter.name,
    RowItem.season.name,
    RowItem.spike.name,
    RowItem.index_load.name,
    RowItem.index_velocity.name,
    RowItem.tire_type.name,
    RowItem.run_flat.name,
    RowItem.inscription_on_the_side.name,
    RowItem.construction_type.name,
    RowItem.axis.name,
    RowItem.layering.name,
    RowItem.intimacy.name,
    RowItem.camera_type.name,
    RowItem.us_aff_designation.name,
    RowItem.disk_thickness.name,
    RowItem.slot_count.name,
    RowItem.pcd1.name,
    RowItem.pcd2.name,
    RowItem.eet.name,
    RowItem.central_diameter.name,
    RowItem.model.name,
    RowItem.mark.name,
)


def _cell(body: dict[str, Any], head: list[str], title: str) -> Any:
    return body[f"cell(1,{head.index(title)})"]


def test_for_full_includes_characteristics() -> None:
    """в шаблоне есть колонки характеристик шин и дисков."""
    fields = {ColumnHelper(column).field for column in ForFull().columns()}
    assert set(_CHARACTERISTIC_FIELDS) <= fields


def test_for_full_does_not_exclude_rows() -> None:
    """полный шаблон не отфильтровывает пустой остаток."""
    assert ForFull().exclude() == {}


def test_xls_write_for_full(tmp_path: Any) -> None:
    """полный шаблон пишет коды, характеристики и цены."""
    row = {
        **write_data[0],
        "height_percent": "40",
        "season": "зима",
        "spike": "шип",
        "pcd1": 112,
        "eet": 45,
        "slot_count": 5,
        "layering": "14PR",
    }
    fake_driver = FakeXlwtDriver()
    result_folder = str(tmp_path)
    XlsWriter(
        fake_driver,
        [row],
        template=ForFull,
        result_folder=result_folder,
    ).write()
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    head = fake_driver.head

    assert fake_driver.file_name == f"price_full_{now}.xlsx"
    assert fake_driver.folder == result_folder
    assert _cell(fake_driver.body, head, "Номенклатура") == "225/40R18 Crossleader 92Y"
    assert _cell(fake_driver.body, head, "Ширина") == "225"
    assert _cell(fake_driver.body, head, "Профиль") == "40"
    assert _cell(fake_driver.body, head, "Диаметр") == "18"
    assert _cell(fake_driver.body, head, "Сезон") == "зима"
    assert _cell(fake_driver.body, head, "Шип") == "шип"
    assert _cell(fake_driver.body, head, "Индекс нагрузки") == "92"
    assert _cell(fake_driver.body, head, "Индекс скорости") == "Y"
    assert _cell(fake_driver.body, head, "PCD") == 112
    assert _cell(fake_driver.body, head, "ET") == 45
    assert _cell(fake_driver.body, head, "Кол-во отверстий") == 5
    assert _cell(fake_driver.body, head, "Слойность") == "14PR"
    assert _cell(fake_driver.body, head, "Цена") == 3980.0
    assert _cell(fake_driver.body, head, "Марка") == "CROSSLEADER"
    assert _cell(fake_driver.body, head, "Модель") == "DSU02"
