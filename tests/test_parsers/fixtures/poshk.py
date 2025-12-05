"""
fixtures for Poshk vendor
"""


def poshk_one_item_result():
    """one file, one price row parse result"""
    return {
        "file_prices\\poshk\\price.xls": [
            {
                "code": "УТ-00017389",
                "title": "10-16.5 Nortec ER-218 10PR 135B TL спецшина, , шт",
                "price_purchase": 4856.0,
                "rest_count": 10.0,
            }
        ]
    }
