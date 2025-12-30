"""
Точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
"""

import logging
import sys

from core.exceptions import SupplierNotHavePricesError
from core.log_message import print_log
from parsers.all_vendors import all_vendors
from parsers.common_price import CommonPrice
from parsers.common_price_output import CommonPriceOut
from parsers.vendors.zapaska_tire import load_data
from run_dialog import AnswerResult, ask_action


def main() -> None:
    """
    entry point
    :return:
    """
    while True:
        response_processing()


def response_processing() -> None:
    """Ask questions"""
    try:
        match ask_action():
            case AnswerResult.MAKE_PRICE_BY_SUPPLIER:
                run_make_price_by_supplier()
            case AnswerResult.UPDATE_ZAPASKA_DATA:
                run_upload_zapaska_data()
            case AnswerResult.EXIT:
                sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)                  


def run_make_price_by_supplier() -> None:
    """Make common price list by price list supplier's"""
    try:
        common_price = CommonPrice()
        common_price.parse_all_vendors(all_vendors())
        CommonPriceOut(common_price.get_result()).write_all_prices()
    except SupplierNotHavePricesError as exc:
        print_log(f"{exc}", level=logging.WARNING)
        sys.exit(1)
   


def run_upload_zapaska_data() -> None:
    """Load zapaska data from api"""
    load_data()
    print_log('*** Данные успешно загружены. ***\n')


if __name__ == '__main__':
    main()
