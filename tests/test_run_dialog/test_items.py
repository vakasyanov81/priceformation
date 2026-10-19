"""tests for menu items"""

from run_dialog import MENU_ITEMS
from run_dialog.items import ACTIVATION_KEY, ANSWER_MAP, AnswerResult, index_by_key


def test_answer_map_keys() -> None:
    """пункты меню соответствуют ожидаемым действиям"""
    assert ANSWER_MAP['1'] == AnswerResult.MAKE_PRICE_BY_SUPPLIER
    assert ANSWER_MAP['2'] == AnswerResult.UPDATE_ALL_SUPPLIER_PRICES
    assert ANSWER_MAP['4'] == AnswerResult.SHOW_HELP
    assert ANSWER_MAP['q'] == AnswerResult.EXIT


def test_menu_items_order_and_keys() -> None:
    """клавиши назначаются по порядку расположения; активация поставщиков занимает номер 3"""
    keys = [menu_item.key for menu_item in MENU_ITEMS]
    assert keys == ['1', '2', '4', 'q']
    assert ACTIVATION_KEY == '3'
    assert [menu_item.action for menu_item in MENU_ITEMS] == list(ANSWER_MAP.values())


def test_index_by_key() -> None:
    """Клавиша быстрого выбора даёт индекс пункта; пустая/чужая — None."""
    assert index_by_key('1') == 0
    assert index_by_key('2') == 1
    assert index_by_key('4') == 2
    assert index_by_key('q') == 3
    assert index_by_key('3') is None
    assert index_by_key('') is None
