"""
write template for drom.ru
"""

from parsers.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import IWriteTemplate


class ForDrom(IWriteTemplate):
    """write template for drom.ru"""

    __COLUMNS__ = [
        {"Тип товара": {"style": {"width": 40}, "field": RowItem.type_production.name}},
        {"Бренд": {"style": {"width": 30}, "field": RowItem.manufacturer.name}},
        {"Номенклатура": {"style": {"width": 30}, "field": RowItem.title.name}},
        {"Сезон": {"field": RowItem.season.name}},
        {"Шип": {"field": RowItem.spike.name}},
        {"Цена": {"field": RowItem.price_markup.name}, "format": "@"},
        {"Остаток": {"field": RowItem.rest_count.name}},
        {"Наличие": {"field": RowItem.available.name, "default_value": "В наличии"}},
        {"Срок доставки": {"field": RowItem.delivery_period.name}},
        {"Состояние": {"field": RowItem.condition.name, "default_value": "Новое"}},
    ]

    __FILE__ = "price_drom_{now}.xlsx"

    __EXCLUDE__ = {RowItem.rest_count.name: [None, ""]}
