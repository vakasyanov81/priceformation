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
                "code": 87674341266.0,
                "title": "CROSSLEADER  225/40/18  Y 92 DSU02",
                "manufacturer_name": "CROSSLEADER",
                "model": "DSU02",
                "diameter": "15",
                "width": "31",
                "height_percent": "10.5",
                "index_velocity": "Y",
                "index_load": "92",
                "rest_count": 4.0,
                "price_purchase": 3457.0,
                "price_recommended": 0,
            }
        ]
    }
