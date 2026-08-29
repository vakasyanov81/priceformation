"""
Точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
3. Отчёт о дублях
4...
"""

import sys

from cfg import init_cfg
from cfg.zapaska_api import get_zapaska_api_config
from core.async_utils import try_call
from core.log_message import print_log
from parsers.all_vendors import all_vendors
from parsers.common_price import CommonPrice
from parsers.common_price_output import CommonPriceOut
from parsers.remote.zapaska_client import load_remote_vendor_data
from run_dialog import AnswerResult, ask_action


def main() -> None:
    """
    entry point
    :return:
    """
    init_cfg()
    while True:
        if not response_processing():
            break
    sys.exit(0)


def response_processing() -> bool:
    """Ask questions"""
    continuation_of_execution = True
    match ask_action():
        case AnswerResult.MAKE_PRICE_BY_SUPPLIER:
            try_call(run_make_price_by_supplier)
        case AnswerResult.UPDATE_ZAPASKA_DATA:
            try_call(run_upload_zapaska_data)
        case AnswerResult.REPORT_DOUBLES:
            try_call(run_report_doubles)
        case AnswerResult.EXIT:
            continuation_of_execution = False
    return continuation_of_execution


def run_make_price_by_supplier() -> None:
    """Make common price list by price list supplier's"""
    common_price = CommonPrice()
    common_price.parse_all_vendors(all_vendors())
    CommonPriceOut(common_price.parsed_items).write_all_prices()


def run_upload_zapaska_data() -> None:
    """Load zapaska data from api"""
    load_remote_vendor_data(api=get_zapaska_api_config())
    print_log("*** Данные успешно загружены. ***\n")


def run_report_doubles() -> None:
    """Parse supplier prices and write duplicates report."""
    common_price = CommonPrice()
    common_price.parse_all_vendors(all_vendors())
    report_path = CommonPriceOut(common_price.parsed_items).write_doubles_report()
    print_log(f"*** Отчёт о дублях сформирован. ***\n{report_path}\n")


if __name__ == "__main__":
    main()
