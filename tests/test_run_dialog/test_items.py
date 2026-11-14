"""tests for menu items"""

from app.run_dialog import MENU_ITEMS
from app.run_dialog.items import ACTIVATION_KEY, ANSWER_MAP, AnswerResult, _assign_keys, index_by_key


def test_answer_map_keys() -> None:
    """пункты меню соответствуют ожидаемым действиям"""
    assert ANSWER_MAP['1'] == AnswerResult.MAKE_PRICE_BY_SUPPLIER
    assert ANSWER_MAP['2'] == AnswerResult.UPDATE_ALL_SUPPLIER_PRICES
    assert ANSWER_MAP['4'] == AnswerResult.SHOW_HELP
    assert ANSWER_MAP['q'] == AnswerResult.EXIT


def test_assigned_keys_reserve_activation_before_help() -> None:
    """Повторный расчёт проверяет функцию, а не сохранённые при импорте константы."""
    keys, activation = _assign_keys()
    assert keys == {
        AnswerResult.MAKE_PRICE_BY_SUPPLIER: '1',
        AnswerResult.UPDATE_ALL_SUPPLIER_PRICES: '2',
        AnswerResult.SHOW_HELP: '4',
        AnswerResult.EXIT: 'q',
    }
    assert activation == '3'


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
