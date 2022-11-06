# -*- coding: utf-8 -*-
"""
точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
"""
__author__ = "Kasyanov V.A."

from parsers.common_price import CommonPrice
from parsers.base_parser.base_parser import SupplierNotHavePrices
from core.log_message import print_log


def run():
    """
    entry point
    :return:
    """
    try:
        common_price = CommonPrice()
        common_price.parse_all_vendors()
        common_price.write_all_prices()
    except SupplierNotHavePrices as exc:
        print_log(f"{exc}", level="WARNING")
        exit(1)


if __name__ == '__main__':
    run()
