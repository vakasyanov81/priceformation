# -*- coding: utf-8 -*-
"""
fixtures for four_tochki sheet2 vendor
"""
__author__ = "Kasyanov V.A."


def four_tochki_one_item_result():
    """ one file, one price row parse result """
    return {
        "file_prices\\four_tochki\\price.xlsx": [
            {
                'code': 'WHS198858', 'manufacturer_name': 'Alcasta', 'model': 'M35', 'width': 6.5, 'diameter': 16,
                'slot_count': 5, 'pcd1': 114.3, 'et': 45, 'central_diameter': 60.1, 'color': 'MBMF', 'rest_count': 4,
                'price_recommended': 8261, 'price_purchase': 7210
            }
        ]
    }
