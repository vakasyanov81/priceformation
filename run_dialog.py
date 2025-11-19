from enum import Enum

from src.cfg.color import Colors
from src.core.log_message import print_log


class AnswerResult(Enum):
    """Main actions"""

    MAKE_PRICE_BY_SUPPLIER = "MakePriceBySupplier"
    UPDATE_ZAPASKA_DATA = "UpdateZapaskaData"
    EXIT = "Exit"


def ask_action() -> AnswerResult:
    """Main console menu"""
    _msg = (
        f"{Colors.BOLD}"
        "1 — сформировать общий прайс по прайсам поставщиков \n"
        "2 — Выгрузить прайсы запаски по API\n"
        f"q — выход {Colors.END_COLOR}"
    )
    while True:
        _answer = AnswerMap.get(input(_msg).strip().lower())
        if _answer:
            return _answer
        print_log("Не понял, давай ещё раз. \n")


AnswerMap = {
    "1": AnswerResult.MAKE_PRICE_BY_SUPPLIER,
    "2": AnswerResult.UPDATE_ZAPASKA_DATA,
    "q": AnswerResult.EXIT,
}
