# -*- coding: utf-8 -*-
"""
write template for drom.ru
"""

__author__ = "Kasyanov V.A."
from parsers.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import IWriteTemplate


class ForDrom(IWriteTemplate):
    """write template for drom.ru"""

    __COLUMNS__ = [
        {"Тип товара": {"style": {"width": 40}, "field": RowItem.__TYPE_PRODUCTION__}},
        {"Бренд": {"style": {"width": 30}, "field": RowItem.__MANUFACTURER_NAME__}},
        {"Номенклатура": {"style": {"width": 30}, "field": RowItem.__TITLE__}},
        {"Сезон": {"field": RowItem.__SEASON__}},
        {"Шип": {"field": RowItem.__SPIKE__}},
        {"Цена": {"field": RowItem.__PRICE_WITH_MARKUP__}},
        {"Остаток": {"field": RowItem.__REST_COUNT__}},
        {"Наличие": {"field": RowItem.__AVAILABLE__, "default_value": "В наличии"}},
        {"Срок доставки": {"field": RowItem.__DELIVERY_PERIOD__}},
        {"Состояние": {"field": RowItem.__CONDITION__, "default_value": "Новое"}},
    ]

    __FILE__ = "price_drom_{now}.xlsx"

    __EXCLUDE__ = {RowItem.__REST_COUNT__: [None, ""]}
