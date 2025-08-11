from enum import Enum

from src.cfg.color import Colors
from src.core.log_message import print_log


class AnswerResult(Enum):
    """Main actions"""

    MAKE_DB_MIGRATION = "MakeDBMigration"
    MAKE_PRICE_BY_SUPPLIER = "MakePriceBySupplier"
    SAVE_PRICE_TO_DB = "SavePriceToDB"
    UPDATE_ZAPASKA_DATA = "UpdateZapaskaData"
    EXIT = "Exit"


def ask_action() -> AnswerResult:
    """Main console menu"""
    _msg = (
        f"{Colors.BOLD}1 — миграция базы данных \n"
        "2 — сформировать общий прайс по прайсам поставщиков \n"
        "3 — записать номенклатуру поставщика в базу данных \n"
        "4 — Выгрузить прайсы запаски по API\n"
        f"q — выход {Colors.END_COLOR}"
    )
    while True:
        _answer = AnswerMap.get(input(_msg).strip().lower())
        if _answer:
            return _answer
        print_log("Не понял, давай ещё раз. \n")


AnswerMap = {
    "1": AnswerResult.MAKE_DB_MIGRATION,
    "2": AnswerResult.MAKE_PRICE_BY_SUPPLIER,
    "3": AnswerResult.SAVE_PRICE_TO_DB,
    "4": AnswerResult.UPDATE_ZAPASKA_DATA,
    "q": AnswerResult.EXIT,
}
