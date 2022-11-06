# -*- coding: utf-8 -*-
"""
write template for internal use
"""
__author__ = "Kasyanov V.A."

from parsers.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import IWriteTemplate


class ForInner(IWriteTemplate):
    """ write template for internal use """
    __COLUMNS__ = [
        {
            "Категория": {
                "style": {
                    "width": 256 * 10
                },
                "field": RowItem.__TYPE_PRODUCTION__
            }
        },
        {
            "Бренд": {
                "style": {
                    "width": 356 * 15
                },
                "field": RowItem.__MANUFACTURER_NAME__
            }
        },
        {
            "Номенклатура": {
                "style": {
                    "width": 256 * 100
                },
                "field": RowItem.__TITLE__
            }
        },
        {
            "Цена закуп.": {
                "style": {
                    "width": 256 * 15
                },
                "field": RowItem.__PRICE_PURCHASE__
            }
        },
        {
            "Цена": {
                "field": RowItem.__PRICE_WITH_MARKUP__
            }
        },
        {
            "Рекомендуемая Цена": {
                "style": {
                    "width": 256 * 25
                },
                "field": RowItem.__PRICE_RECOMMENDED__
            }
        },
        {
            "Наценка %": {
                "style": {
                    "width": 256 * 15
                },
                "field": RowItem.__PERCENT__
            }
        },
        {
            "Остаток": {
                "field": RowItem.__REST_COUNT__
            }
        },
        {
            "Поставщик": {
                "style": {
                    "width": 256 * 15
                },
                "field": RowItem.__SUPPLIER_NAME_COLUMN__
            }
        }
    ]

    __COLOR__ = {
        "by_column": RowItem.__SUPPLIER_NAME_COLUMN__,
        "with_map": {
            "Пошк": "blue",
            "Мим": "#f7d5d2",
            "Запаска (остатки)": "#99706d",
            "Пионер": "#658c68"
        },
        "set_to_column_index": 0
    }

    __FILE__ = 'price_{now}.xlsx'

    __EXCLUDE__ = {}
