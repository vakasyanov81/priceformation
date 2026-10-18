"""Объединение складов одной группы для прайса дрома."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.common_price_warehouses import merge_warehouse_rows

_NSK: dict[str, Any] = {'warehouse_group': 'novosibirsk', 'warehouse_name': 'Новосибирск'}


def _row(code: str, price: float, rest: int, **warehouse: Any) -> RowItem:
    return RowItem(
        {
            'code': code,
            'supplier_name': 'Форточки',
            'title': f'Шина {code}',
            'price_markup': price,
            'rest_count': rest,
            **(_NSK | warehouse),
        },
    )


def test_same_price_rests_are_summed() -> None:
    """Одинаковая цена на складах группы — остатки складываются в одну строку."""
    rows = [
        _row('A', 5000, 3),
        _row('A', 5000, 4, warehouse_name='ОХ г. Новосибирск Чехова'),
    ]

    merged = merge_warehouse_rows(rows)

    assert len(merged) == 1
    assert merged[0].pricing.price_markup == 5000
    assert merged[0].stock.rest_count == 7


def test_different_prices_take_cheapest_with_its_rest_only() -> None:
    """Разные цены — берём наименьшую с её остатком, остальные остатки не суммируем."""
    rows = [
        _row('A', 5300, 10),
        _row('A', 5000, 2),
        _row('A', 5100, 6),
    ]

    merged = merge_warehouse_rows(rows)

    assert len(merged) == 1
    assert merged[0].pricing.price_markup == 5000
    assert merged[0].stock.rest_count == 2


def test_cheapest_price_shared_by_several_rows_sums_their_rests() -> None:
    """Если наименьшую цену дают несколько складов, их остатки складываются, более дорогие — нет."""
    rows = [
        _row('A', 5000, 2),
        _row('A', 5000, 3),
        _row('A', 6000, 9),
    ]

    merged = merge_warehouse_rows(rows)

    assert len(merged) == 1
    assert merged[0].stock.rest_count == 5


def test_rows_without_group_are_kept_as_is() -> None:
    """Склады вне группы (Томск, Новокузнецк) не объединяются и остаются отдельными строками."""
    rows = [
        _row('A', 5000, 1, warehouse_group=None, warehouse_name='Томск'),
        _row('A', 5000, 2, warehouse_group=None, warehouse_name='Новокузнецк 3'),
    ]

    merged = merge_warehouse_rows(rows)

    assert merged == rows


def test_different_positions_are_not_merged_and_order_is_kept() -> None:
    """Разные позиции не склеиваются; порядок строк — как в исходном списке."""
    rows = [
        _row('A', 5000, 1),
        _row('B', 7000, 2),
        _row('A', 5000, 3),
    ]

    merged = merge_warehouse_rows(rows)

    assert [row.identity.code for row in merged] == ['A', 'B']
    assert [row.stock.rest_count for row in merged] == [4, 2]


def test_source_rows_are_not_changed() -> None:
    """Прайс со своими складами использует те же строки: объединение их не меняет."""
    first = _row('A', 5000, 3)
    second = _row('A', 5000, 4)

    merge_warehouse_rows([first, second])

    assert first.stock.rest_count == 3
    assert second.stock.rest_count == 4


def test_same_code_of_different_suppliers_is_not_merged() -> None:
    """Объединение внутри поставщика: одинаковый код и группа у разных поставщиков — разные позиции."""
    other = RowItem({**_row('A', 5000, 4).to_dict(), 'supplier_name': 'Другой'})

    merged = merge_warehouse_rows([_row('A', 5000, 3), other])

    assert [row.stock.rest_count for row in merged] == [3, 4]


def test_missing_rest_counts_as_zero_in_sum() -> None:
    """Склад без остатка не прибавляет к сумме единицу."""
    no_rest = RowItem({**_row('A', 5000, 0).to_dict(), 'rest_count': None})

    merged = merge_warehouse_rows([_row('A', 5000, 3), no_rest])
    assert merged[0].stock.rest_count == 3
