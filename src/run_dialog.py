"""CLI dialog for main console actions."""

from enum import Enum

from cfg.color import Colors
from core.log_message import print_log


class AnswerResult(Enum):
    """Main actions"""

    MAKE_PRICE_BY_SUPPLIER = "MakePriceBySupplier"
    UPDATE_ZAPASKA_DATA = "UpdateZapaskaData"
    REPORT_DOUBLES = "ReportDoubles"
    EXIT = "Exit"


ANSWER_MAP = {
    "1": AnswerResult.MAKE_PRICE_BY_SUPPLIER,
    "2": AnswerResult.UPDATE_ZAPASKA_DATA,
    "3": AnswerResult.REPORT_DOUBLES,
    "q": AnswerResult.EXIT,
}


def ask_action() -> AnswerResult:
    """Main console menu"""
    msg = (
        f"{Colors.BOLD}"
        "1 — сформировать общий прайс по прайсам поставщиков \n"
        "2 — Выгрузить прайсы запаски по API\n"
        "3 — отчёт о дублях\n"
        f"q — выход {Colors.END_COLOR}"
    )
    while True:
        answer = ANSWER_MAP.get(input(msg).strip().lower())
        if answer:
            return answer
        print_log("Не понял, давай ещё раз. \n")
