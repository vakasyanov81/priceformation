# -*- coding: utf-8 -*-
"""
write template for internal use
"""
__author__ = "Kasyanov V.A."

from src.parsers.row_item.row_item import RowItem
from src.parsers.writer.templates.iwrite_template import IWriteTemplate


class ForInner(IWriteTemplate):
    """write template for internal use"""

    __COLUMNS__ = [
        {
            "Тип товара": {
                "style": {"width": 256 * 10},
                "field": RowItem.__TYPE_PRODUCTION__,
            }
        },
        {
            "Бренд": {
                "style": {"width": 356 * 15},
                "field": RowItem.__MANUFACTURER_NAME__,
            }
        },
        {"Номенклатура": {"style": {"width": 256 * 100}, "field": RowItem.__TITLE__}},
        {"Сезон": {"field": RowItem.__SEASON__}},
        {"Шип": {"field": RowItem.__SPIKE__}},
        {"Цена закуп.": {"style": {"width": 256 * 15}, "field": RowItem.__PRICE_PURCHASE__, "format": "@"}},
        {"Цена": {"field": RowItem.__PRICE_WITH_MARKUP__}},
        {"Рекомендуемая Цена": {"style": {"width": 256 * 25}, "field": RowItem.__PRICE_RECOMMENDED__, "format": "@"}},
        {"Наценка %": {"style": {"width": 256 * 15}, "field": RowItem.__PERCENT__}},
        {"Остаток": {"field": RowItem.__REST_COUNT__}},
        {
            "Поставщик": {
                "style": {"width": 256 * 15},
                "field": RowItem.__SUPPLIER_NAME_COLUMN__,
            }
        },
        {"Наличие": {"field": RowItem.__AVAILABLE__, "default_value": "В наличии"}},
        {"Срок доставки": {"field": RowItem.__DELIVERY_PERIOD__}},
        {"Состояние": {"field": RowItem.__CONDITION__, "default_value": "Новое"}},
    ]

    __COLOR__ = {
        "by_column": RowItem.__SUPPLIER_NAME_COLUMN__,
        "with_map": {
            "Пошк": "blue",
            "Мим": "#f7d5d2",
            "Запаска (остатки)": "#99706d",
            "Форточки": "#658c68",
        },
        "set_to_column_index": 0,
    }

    __FILE__ = "price_{now}.xlsx"

    __EXCLUDE__ = {}
