# -*- coding: utf-8 -*-
"""
fixtures for four_tochki sheet1 vendor
"""
__author__ = "Kasyanov V.A."


def four_tochki_one_item_result():
    """ one file, one price row parse result """
    return {
        "file_prices\\four_tochki\\price.xlsx": [
            {
                'code': '527719', 'manufacturer_name': 'BFGoodrich', 'model': 'Advantage', 'width': 205,
                'height_percent': 55, 'diameter': 'R16', 'index_load': '94W', 'ext_diameter': 0,
                'american_affiliation_designation': None, 'rest_count': 'более 40', 'price_recommended': 7340,
                'price_purchase': 5772, 'tire_type': 'Легковая'
            },
            {
                'code': '875678', 'manufacturer_name': 'BFGoodrich', 'model': 'All Terrain T/A KO2', 'width': 10.5,
                'height_percent': 0, 'diameter': 'R15', 'index_load': '109S', 'ext_diameter': 31,
                'american_affiliation_designation': 'LT', 'rest_count': 10, 'price_recommended': 24870,
                'price_purchase': 19577, 'tire_type': 'Легковая'
            },
            {
                'code': '527725', 'manufacturer_name': 'BFGoodrich', 'model': 'Route Control D', 'width': 235,
                'height_percent': 75, 'diameter': 'R17.5', 'index_load': '132/130M', 'ext_diameter': 0,
                'american_affiliation_designation': None, 'rest_count': 'более 40', 'price_recommended': 23010,
                'price_purchase': 21912, 'tire_type': 'Грузовая'
            }
        ]
    }
