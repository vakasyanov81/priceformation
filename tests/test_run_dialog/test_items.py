"""tests for menu items"""

from run_dialog import MENU_ITEMS
from run_dialog.items import ANSWER_MAP, AnswerResult, index_by_key


def test_answer_map_keys() -> None:
    """пункты меню соответствуют ожидаемым действиям"""
    assert ANSWER_MAP['1'] == AnswerResult.MAKE_PRICE_BY_SUPPLIER
    assert ANSWER_MAP['2'] == AnswerResult.UPDATE_ZAPASKA_DATA
    assert ANSWER_MAP['3'] == AnswerResult.UPDATE_FOUR_TOCHKI_DATA
    assert ANSWER_MAP['5'] == AnswerResult.SHOW_HELP
    assert ANSWER_MAP['6'] == AnswerResult.REPORT_DOUBLES
    assert ANSWER_MAP['7'] == AnswerResult.FETCH_MAIL_PRICES
    assert ANSWER_MAP['q'] == AnswerResult.EXIT


def test_menu_items_order_and_keys() -> None:
    """порядок пунктов и клавиши строкового ввода стабильны"""
    keys = [menu_item.key for menu_item in MENU_ITEMS]
    assert keys == ['1', '8', '2', '3', '5', '6', '7', 'q']
    assert [menu_item.action for menu_item in MENU_ITEMS] == list(ANSWER_MAP.values())


def test_index_by_key() -> None:
    """Клавиша быстрого выбора даёт индекс пункта; пустая/чужая — None."""
    assert index_by_key('1') == 0
    assert index_by_key('8') == 1
    assert index_by_key('2') == 2
    assert index_by_key('3') == 3
    assert index_by_key('5') == 4
    assert index_by_key('6') == 5
    assert index_by_key('7') == 6
    assert index_by_key('q') == 7
    assert index_by_key('9') is None
    assert index_by_key('') is None
