# -*- coding: utf-8 -*-
"""
stubs for tests for Zapaska vendor
"""
__author__ = "Kasyanov V.A."

from parsers.row_item.row_item import RowItem


def zapaska_one_item_result():
    """one file, one price row parse result"""
    return (
        {
            "file_prices\\zapaska\\rest_1.xls": [
                {
                    "code": "00002",
                    "title": "00 Сельх.шины",
                    "rest_count": 17.0,
                    "price_purchase": 4012.4,
                    "hash_title": "4d454469fa9bb61110e92a2317896b91",
                    "codes": ["00002"],
                    "sup_name": "Запаска (остатки)",
                }
            ]
        },
        [
            RowItem(
                {
                    "code": "00002",
                    "brand": "АШК",
                    "title": "00 Сельх.шины",
                    "price_recommended": 4201.0,
                    "hash_title": "4d454469fa9bb61110e92a2317896b91",
                    "codes": ["00002"],
                    "sup_name": "Запаска",
                }
            )
        ],
    )


def zapaska_2file_result():
    """two files, two price row parse result"""
    return (
        {
            "file_prices\\zapaska\\rest_1.xls": [
                {
                    "code": "00002",
                    "title": "00 Сельх.шины",
                    "rest_count": 17.0,
                    "price_purchase": 4012.4,
                    "hash_title": "4d454469fa9bb61110e92a2317896b91",
                    "codes": ["00002"],
                    "sup_name": "Запаска (остатки)",
                }
            ],
            "file_prices\\zapaska\\rest_2.xls": [
                {
                    "code": "00003",
                    "title": "00 Сельх.шины__1",
                    "rest_count": 10.0,
                    "price_purchase": 4012.4,
                    "hash_title": "d25c14e72f2a951230173b9a68f9d294",
                    "codes": ["00003"],
                    "sup_name": "Запаска (остатки)",
                }
            ],
        },
        [
            RowItem(
                {
                    "code": "00002",
                    "brand": "АШК",
                    "title": "00 Сельх.шины",
                    "price_recommended": 4201.0,
                    "hash_title": "4d454469fa9bb61110e92a2317896b91",
                    "codes": ["00002"],
                    "sup_name": "Запаска",
                }
            ),
            RowItem(
                {
                    "code": "00003",
                    "brand": "АШК",
                    "title": "00 Сельх.шины__1",
                    "price_recommended": 4251.0,
                    "hash_title": "d25c14e72f2a951230173b9a68f9d294",
                    "codes": ["00003"],
                    "sup_name": "Запаска",
                }
            ),
        ],
    )


__ALL__ = [zapaska_one_item_result, zapaska_2file_result]
