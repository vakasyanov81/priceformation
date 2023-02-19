# -*- coding: utf-8 -*-
"""
fixtures for writer
"""
__author__ = "Kasyanov V.A."

from parsers.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import IWriteTemplate

write_data = [
    {
        "code": 87674341266.0, "title": "225/40R18 Crossleader 92Y", "mark": "CROSSLEADER", "model": "DSU02",
        "diameter": "18", "width": "225", "profile": "40", "index_velocity": "Y", "index_load": "92",
        "rest_count": 4.0, "price_purchase": 3457.0, "price_recommended": "", "sup_name": "Мим",
        "price_markup": 3980.0, "type_production": "Автошина", "percent": 15.13
    }
]

result_body_drom = {
    "cell(1,0)": "Автошина",
    "cell(1,2)": "225/40R18 Crossleader 92Y",
    "cell(1,3)": 3980.0,
    "cell(1,4)": 4.0,
    "cell(1,5)": "В наличии",
    "cell(1,7)": "Новое"
}

result_body_inner = {
    "cell(1,0)": "Автошина",
    "cell(1,2)": "225/40R18 Crossleader 92Y",
    "cell(1,3)": 3457.0,
    "cell(1,4)": 3980.0,
    "cell(1,6)": 15.13,
    "cell(1,7)": 4.0,
    "cell(1,8)": "Мим"
}


class FixtureTemplate(IWriteTemplate):
    """ fixture template """
    __COLUMNS__ = [
        {
            "Номенклатура": {
                "field": RowItem.__TITLE__
            }
        },
        {
            "Цена": {
                "field": RowItem.__PRICE_WITH_MARKUP__
            }
        },
        {
            "Остаток": {
                "field": RowItem.__REST_COUNT__
            }
        }
    ]
