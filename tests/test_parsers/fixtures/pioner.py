# -*- coding: utf-8 -*-
"""
fixtures for Pioner vendor
"""
__author__ = "Kasyanov V.A."


def pioner_one_item_result():
    """one file, one price row parse result"""
    return {
        "file_prices\\pioner\\price.xls": [
            {
                "title": "Автокамера 14.00-24",
                "price_purchase": "2200,0 Руб.",
                "rest_count": 20.0,
                "reserve_count": "",
                "sup_name": "Пионер",
                "price_markup": 2350.0,
            }
        ]
    }


def pioner_one_item_result_with_categories():
    """one file, one price row parse result with categories"""
    return {
        "file_prices\\pioner\\price.xls": [
            {"title": "Автошины"},
            {"title": "Автошины TRIANGLE"},
            {
                "title": "185/75R16C Triangle TR646 104/102Q 8PR TL",
                "price_purchase": 2200.0,
                "price_recommended": 2350.0,
                "rest_count": 20.0,
                "reserve_count": "",
                "sup_name": "Пионер",
                "price_markup": 2350.0,
                "brand": None,
                "percent": 6.82,
            },
        ]
    }
