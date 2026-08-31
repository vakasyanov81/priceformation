"""
write template with all parsed fields for CLI
"""

from typing import ClassVar

from parsers.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import IWriteTemplate, WriteColumns

_SPECS: tuple[tuple[str, str], ...] = (
    ("Тип товара", RowItem.type_production.name),
    ("Бренд", RowItem.manufacturer.name),
    ("Brand", RowItem.brand.name),
    ("Марка", RowItem.mark.name),
    ("Модель", RowItem.model.name),
    ("Номенклатура", RowItem.title.name),
    ("Код", RowItem.code.name),
    ("Код производителя", RowItem.code_man.name),
    ("Артикул", RowItem.code_art.name),
    ("Поставщик", RowItem.supplier_name.name),
    ("Сезон", RowItem.season.name),
    ("Шип", RowItem.spike.name),
    ("Ширина", RowItem.width.name),
    ("Профиль", RowItem.height_percent.name),
    ("Диаметр", RowItem.diameter.name),
    ("Внешний диаметр", RowItem.ext_diameter.name),
    ("Индекс нагрузки", RowItem.index_load.name),
    ("Индекс скорости", RowItem.index_velocity.name),
    ("Тип шины", RowItem.tire_type.name),
    ("RunFlat", RowItem.run_flat.name),
    ("Надпись на боковине", RowItem.inscription_on_the_side.name),
    ("Тип конструкции", RowItem.construction_type.name),
    ("Ось", RowItem.axis.name),
    ("Слойность", RowItem.layering.name),
    ("Камерность", RowItem.intimacy.name),
    ("Тип камеры", RowItem.camera_type.name),
    ("US обозначение", RowItem.us_aff_designation.name),
    ("Толщина диска", RowItem.disk_thickness.name),
    ("Кол-во отверстий", RowItem.slot_count.name),
    ("PCD", RowItem.pcd1.name),
    ("PCD2", RowItem.pcd2.name),
    ("ET", RowItem.eet.name),
    ("DIA", RowItem.central_diameter.name),
    ("Крепеж", RowItem.fastener.name),
    ("Тип диска", RowItem.disk_type.name),
    ("Вид диска", RowItem.disk_type_1.name),
    ("Цвет", RowItem.color.name),
    ("Основной цвет", RowItem.main_color.name),
    ("Цена закуп.", RowItem.price_opt.name),
    ("Цена", RowItem.price_markup.name),
    ("Рекомендуемая Цена", RowItem.price_recommended.name),
    ("Наценка %", RowItem.percent_markup.name),
    ("Остаток", RowItem.rest_count.name),
    ("Резерв", RowItem.reserve_count.name),
    ("Наличие", RowItem.available.name),
    ("Срок доставки", RowItem.delivery_period.name),
    ("Состояние", RowItem.condition.name),
)


class ForFull(IWriteTemplate):
    """write template with all parsed fields for CLI"""

    __COLUMNS__: ClassVar[WriteColumns] = [{title: {"field": field}} for title, field in _SPECS]
    __FILE__ = "price_full_{now}.xlsx"
