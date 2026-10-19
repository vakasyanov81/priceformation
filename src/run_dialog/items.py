"""Пункты главного меню: действия, подписи и клавиши строкового ввода."""

import dataclasses
from enum import Enum


class AnswerResult(Enum):
    """Main actions"""

    MAKE_PRICE_BY_SUPPLIER = 'MakePriceBySupplier'
    UPDATE_ZAPASKA_DATA = 'UpdateZapaskaData'
    UPDATE_FOUR_TOCHKI_DATA = 'UpdateFourTochkiData'
    REPORT_DOUBLES = 'ReportDoubles'
    FETCH_MAIL_PRICES = 'FetchPricesFromMail'
    UPDATE_ALL_SUPPLIER_PRICES = 'UpdateAllSupplierPrices'
    SHOW_HELP = 'ShowHelp'
    EXIT = 'Exit'


@dataclasses.dataclass(frozen=True)
class MenuItem:
    """Пункт меню: действие и подпись. Клавиша назначается по порядку расположения."""

    action: AnswerResult
    label: str

    @property
    def key(self) -> str:
        """Клавиша быстрого выбора: номер по порядку, для выхода — 'q'."""
        return MENU_KEYS[self.action]


MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem(AnswerResult.MAKE_PRICE_BY_SUPPLIER, 'сформировать общий прайс по прайсам поставщиков'),
    MenuItem(AnswerResult.UPDATE_ALL_SUPPLIER_PRICES, 'обновить прайсы всех поставщиков (API и почта)'),
    MenuItem(AnswerResult.UPDATE_ZAPASKA_DATA, 'Выгрузить прайсы запаски по API'),
    MenuItem(AnswerResult.UPDATE_FOUR_TOCHKI_DATA, 'Выгрузить данные Форточек по API'),
    MenuItem(AnswerResult.SHOW_HELP, 'справка (README)'),
    MenuItem(AnswerResult.REPORT_DOUBLES, 'отчёт о дублях'),
    MenuItem(AnswerResult.FETCH_MAIL_PRICES, 'получить прайсы поставщиков по почте'),
    MenuItem(AnswerResult.EXIT, 'выход'),
)

EXIT_KEY = 'q'


def _assign_keys() -> tuple[dict[AnswerResult, str], str]:
    """Номера по порядку расположения; активация поставщиков стоит перед справкой и получает свой номер."""
    keys: dict[AnswerResult, str] = {}
    number = 0
    activation_key = ''
    for menu_item in MENU_ITEMS:
        if menu_item.action is AnswerResult.SHOW_HELP:
            number += 1
            activation_key = str(number)
        if menu_item.action is AnswerResult.EXIT:
            keys[menu_item.action] = EXIT_KEY
            continue
        number += 1
        keys[menu_item.action] = str(number)
    return keys, activation_key


MENU_KEYS, ACTIVATION_KEY = _assign_keys()

ANSWER_MAP: dict[str, AnswerResult] = {menu_item.key: menu_item.action for menu_item in MENU_ITEMS}


def index_by_key(char: str) -> int | None:
    """Индекс пункта по клавише быстрого выбора, если клавиша известна."""
    if not char:
        return None
    for index, menu_item in enumerate(MENU_ITEMS):
        if menu_item.key == char:
            return index
    return None
