"""Пункты главного меню: действия, подписи и клавиши строкового ввода."""

import dataclasses
from enum import Enum


class AnswerResult(Enum):
    """Main actions"""

    MAKE_PRICE_BY_SUPPLIER = 'MakePriceBySupplier'
    UPDATE_ZAPASKA_DATA = 'UpdateZapaskaData'
    REPORT_DOUBLES = 'ReportDoubles'
    EXIT = 'Exit'


@dataclasses.dataclass(frozen=True)
class MenuItem:
    """Пункт меню: действие, подпись и клавиша для ввода строкой."""

    action: AnswerResult
    label: str
    key: str


MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem(AnswerResult.MAKE_PRICE_BY_SUPPLIER, 'сформировать общий прайс по прайсам поставщиков', '1'),
    MenuItem(AnswerResult.UPDATE_ZAPASKA_DATA, 'Выгрузить прайсы запаски по API', '2'),
    MenuItem(AnswerResult.REPORT_DOUBLES, 'отчёт о дублях', '3'),
    MenuItem(AnswerResult.EXIT, 'выход', 'q'),
)

ANSWER_MAP: dict[str, AnswerResult] = {menu_item.key: menu_item.action for menu_item in MENU_ITEMS}


def index_by_key(char: str) -> int | None:
    """Индекс пункта по клавише быстрого выбора, если клавиша известна."""
    if not char:
        return None
    for index, menu_item in enumerate(MENU_ITEMS):
        if menu_item.key == char:
            return index
    return None
