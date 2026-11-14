"""Главный дубль выбирается общей логикой отбора строки для шаблона."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.common_price.main_double import is_doubtful_price, main_double

_ON_ORDER = 'Под заказ'
_PRIORITY = 'Автоснабжение'
_OTHER = 'Пошк'


def _row(price: int, **fields: Any) -> RowItem:
    return RowItem({'title': 'шина', 'price_markup': price, **fields})


def test_cheapest_wins_among_equal_rows() -> None:
    cheap, dear = _row(10), _row(20)
    assert main_double([dear, cheap]) is cheap


def test_row_with_rest_beats_cheaper_row_without_rest() -> None:
    """Строка без остатка не становится главной, пока в группе есть остаток."""
    no_rest = _row(10)
    with_rest = _row(20, rest_count=1)
    assert main_double([no_rest, with_rest]) is with_rest


def test_priority_supplier_wins_over_cheaper_in_stock() -> None:
    """Приоритетный поставщик важнее наличия и цены у других."""
    priority = _row(20, supplier_name=_PRIORITY, available=_ON_ORDER, rest_count=1)
    other = _row(10, supplier_name=_OTHER, rest_count=1)
    assert main_double([other, priority], (_PRIORITY,)) is priority


def test_in_stock_beats_cheaper_on_order_without_priority() -> None:
    """Без приоритетного поставщика позиция в наличии главнее дешёвой под заказ."""
    on_order = _row(10, available=_ON_ORDER, rest_count=1)
    in_stock = _row(20, rest_count=1)
    assert main_double([on_order, in_stock]) is in_stock


def test_in_stock_beats_fresher_on_order_batch() -> None:
    """Наличие важнее свежести партии: старая позиция в наличии главнее новой под заказ."""
    old_in_stock = _row(10, production_year=2022)
    fresh_on_order = _row(20, production_year=2023, available=_ON_ORDER)
    assert main_double([old_in_stock, fresh_on_order]) is old_in_stock


def test_fresh_row_beats_cheaper_old_batch() -> None:
    """Старая партия дешевле, но главный — более свежая позиция."""
    old = _row(10, production_year=2022)
    new = _row(20, production_year=2023)
    assert main_double([old, new]) is new


def test_row_without_year_counts_as_fresh() -> None:
    """Год пишут только у старых партий: позиция без года свежее любой с годом."""
    old = _row(10, production_year=2023)
    undated = _row(20)
    assert main_double([old, undated]) is undated


def test_cheapest_within_freshest_batch() -> None:
    """Внутри самой свежей партии главная самая дешёвая."""
    old = _row(5, production_year=2021)
    fresh_dear = _row(30, production_year=2023)
    fresh_cheap = _row(20, production_year=2023)
    assert main_double([old, fresh_dear, fresh_cheap]) is fresh_cheap


def test_older_than_marker_loses_to_explicit_year() -> None:
    """«2 года и старше» старее любого явного года."""
    oldest = _row(10, production_year=1)
    dated = _row(20, production_year=2022)
    assert main_double([oldest, dated]) is dated


def test_markdown_is_not_main_while_regular_exists() -> None:
    """Уценка дешевле, но главный — обычный товар."""
    markdown = _row(10, marked_down=True)
    regular = _row(20, production_year=2021)
    assert main_double([markdown, regular]) is regular


def test_all_markdown_still_has_main() -> None:
    """Все уценены — уценка никого не выделяет, главный самый дешёвый."""
    cheap = _row(10, marked_down=True)
    dear = _row(20, marked_down=True)
    assert main_double([dear, cheap]) is cheap


def test_cheapest_in_stock_wins() -> None:
    """Несколько позиций в наличии — главная самая дешёвая."""
    dear = _row(20, available='В наличии', rest_count=1)
    cheap = _row(10, available='В наличии', rest_count=1)
    assert main_double([dear, cheap]) is cheap


def test_all_on_order_keeps_previous_order() -> None:
    """Все под заказ — наличие никого не выделяет, главный самый дешёвый."""
    dear = _row(20, available=_ON_ORDER, rest_count=1)
    cheap = _row(10, available=_ON_ORDER, rest_count=1)
    assert main_double([dear, cheap]) is cheap


def test_zero_main_price_is_not_doubtful() -> None:
    main = _row(100, price_opt=0)
    other = _row(200, price_opt=200)

    assert not is_doubtful_price(other, main)


def test_warehouse_rows_are_merged_before_choice() -> None:
    """Склады одной группы сводятся как для drom: одинаковые цены дают сумму остатков."""
    first = _row(10, code='A', warehouse_group='novosibirsk', rest_count=2)
    second = _row(10, code='A', warehouse_group='novosibirsk', rest_count=3)

    main = main_double([first, second])

    assert main.stock.rest_count == 5
    assert main is not first
