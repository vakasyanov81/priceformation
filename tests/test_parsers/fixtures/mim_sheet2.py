# -*- coding: utf-8 -*-
"""
fixtures for Mim vendor
"""
__author__ = "Kasyanov V.A."


def mim_one_item_result():
    """one file, one price row parse result"""
    return {
        "file_prices\\mim\\price.xlsx": [
            {
                "code": 87331631104.0,
                "title": "some title",
                "manufacturer_name": "HIFLY",
                "model": "HH312",
                "width": "295",
                "height_percent": "75",
                "construction_type": "R",
                "diameter": "22.5",
                "axis": "Ведущая M+S",
                "intimacy": "TL",
                "layering": "PR16",
                "index_load": "146/143",
                "index_velocity": "L",
                "rest_count": 5.0,
                "price_purchase": 23200.0,
                "price_recommended": 23725.0,
                "sup_name": "Мим",
                "price_markup": 0.0,
                "type_production": "Диск",
                "percent": 0,
            }
        ]
    }
