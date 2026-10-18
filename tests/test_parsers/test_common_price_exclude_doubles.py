"""Исключение дублей в шаблоне: одна строка на группу дублей."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.common_price_exclude_doubles import exclude_doubles, is_on_order, pick_double

_AUTOSNAB = 'Автоснабжение'
_POSHK = 'Пошк'
_MIM = 'Мим'
_ON_ORDER = 'Под заказ'


def _double(supplier: str, price: float, rest: int | None, group: int = 1, **fields: Any) -> RowItem:
    row_item = RowItem(
        {
            'supplier_name': supplier,
            'title': f'Шина {supplier}',
            'price_markup': price,
            'rest_count': rest,
            **fields,
        },
    )
    row_item.set_field('group_by_params', group)
    row_item.set_field('is_double', True)
    return row_item


def test_priority_supplier_wins_over_cheaper_in_stock() -> None:
    """Приоритетный поставщик важнее наличия и цены у других."""
    autosnab = _double(_AUTOSNAB, 9000, 2, available=_ON_ORDER)
    rows = [_double(_POSHK, 5000, 4), autosnab]

    picked = pick_double(rows, (_AUTOSNAB,))

    assert picked.vendor.supplier_name == _AUTOSNAB
    assert picked.pricing.price_markup == 9000


def test_priority_order_follows_settings_list() -> None:
    """Первый по списку найденный поставщик выигрывает у второго."""
    rows = [_double(_POSHK, 5000, 4), _double(_AUTOSNAB, 9000, 2)]

    picked = pick_double(rows, (_MIM, _POSHK, _AUTOSNAB))

    assert picked.vendor.supplier_name == _POSHK


def test_in_stock_beats_cheaper_on_order() -> None:
    """Есть позиция в наличии — под заказ игнорируется, даже если дешевле."""
    on_order = _double(_POSHK, 4000, 8, available=_ON_ORDER)
    rows = [on_order, _double(_MIM, 6000, 1)]

    picked = pick_double(rows)

    assert picked.vendor.supplier_name == _MIM


def test_only_on_order_takes_cheapest() -> None:
    """Все под заказ — выбирается самая низкая цена."""
    expensive = _double(_POSHK, 6000, 8, available=_ON_ORDER)
    cheap = _double(_MIM, 5000, 1, available=_ON_ORDER)
    rows = [expensive, cheap]

    assert pick_double(rows).vendor.supplier_name == _MIM


def test_in_stock_cheapest_wins() -> None:
    """Несколько в наличии — берётся меньшая цена с её остатком."""
    rows = [_double(_POSHK, 6000, 8), _double(_MIM, 5000, 1)]

    picked = pick_double(rows)

    assert picked.vendor.supplier_name == _MIM
    assert picked.stock.rest_count == 1


def test_same_price_in_stock_sums_rests_without_touching_source() -> None:
    """Одинаковая цена в наличии — остатки складываются в копию, исходные строки не меняются."""
    first = _double(_POSHK, 5000, 3)
    second = _double(_MIM, 5000, 4)
    on_order = _double('Форточки', 5000, 9, available=_ON_ORDER)
    rows = [first, second, on_order]

    picked = pick_double(rows)

    assert picked.stock.rest_count == 7
    assert picked is not first
    assert first.stock.rest_count == 3


def test_row_without_rest_is_not_picked() -> None:
    """Строка без остатка не выбирается, пока в группе есть остаток — шаблон её бы отбросил."""
    rows = [_double(_AUTOSNAB, 4000, None), _double(_POSHK, 6000, 2)]

    assert pick_double(rows, (_AUTOSNAB,)).vendor.supplier_name == _POSHK


def test_exclude_keeps_one_row_per_group_in_place() -> None:
    """Группа дублей — одна строка на месте первой; строки вне групп не меняются."""
    unique = RowItem({'title': 'Уникальная', 'rest_count': 1})
    group_one = [_double(_POSHK, 6000, 2), _double(_MIM, 5000, 2)]
    second_poshk = _double(_POSHK, 3000, 1, group=2)
    second_group = [second_poshk, _double(_AUTOSNAB, 3500, 1, group=2)]
    first_poshk, first_mim = group_one

    kept = exclude_doubles([first_poshk, unique, *second_group, first_mim], (_AUTOSNAB,))

    assert [row.vendor.supplier_name for row in kept] == [_MIM, None, _AUTOSNAB]
    assert kept[1] is unique


def test_main_double_is_part_of_group() -> None:
    """Главный дубль (double_candidate) входит в группу наравне с остальными."""
    candidate = RowItem({'supplier_name': _MIM, 'price_markup': 4000, 'rest_count': 1})
    candidate.set_field('group_by_params', 1)
    candidate.set_field('double_candidate', True)

    kept = exclude_doubles([_double(_POSHK, 5000, 1), candidate])

    assert [row.vendor.supplier_name for row in kept] == [_MIM]


def test_on_order_detected_by_word_in_available() -> None:
    """Под заказ — по слову «заказ» без учёта регистра; пустое наличие — в наличии."""
    assert is_on_order(RowItem({'available': 'ПОД ЗАКАЗ'}))
    assert not is_on_order(RowItem({'available': 'В наличии'}))
    assert not is_on_order(RowItem({}))
