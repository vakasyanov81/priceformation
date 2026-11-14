"""Расчёт итоговой наценки не теряет точность денег и не делит на ноль."""

import pytest

from domain.battery.item import BatteryItem
from parsers.battery.statistic import BatteryResultStatistic


@pytest.mark.parametrize(
    'purchase, sale',
    [(None, 500), (0, 500), (100, None), (None, None)],
)
def test_unknown_price_pairs_do_not_change_markup_ranges(purchase: int | None, sale: int | None) -> None:
    positions = [
        BatteryItem.from_fields({'price_opt': '100.10', 'price_recommended': '120.12'}),
        BatteryItem.from_fields({'price_opt': purchase, 'price_recommended': sale}),
    ]
    stats = BatteryResultStatistic(positions)
    assert stats.count_items() == 2
    assert stats.real_absolute_markup() == (20.0, 20.0)
    assert stats.real_percents_markup() == (20.0, 20.0)


def test_empty_result_has_zero_statistics() -> None:
    stats = BatteryResultStatistic([])
    assert stats.count_items() == 0
    assert stats.real_absolute_markup() == (0, 0)
    assert stats.real_percents_markup() == (0, 0)


def test_fractional_purchase_price_is_included() -> None:
    stats = BatteryResultStatistic([BatteryItem.from_fields({'price_opt': '0.5', 'price_recommended': '1'})])

    assert stats.real_absolute_markup() == (0.5, 0.5)
    assert stats.real_percents_markup() == (100.0, 100.0)


def test_negative_zero_and_fractional_margins() -> None:
    positions = [
        BatteryItem.from_fields({'price_opt': 100, 'price_recommended': '90.13'}),
        BatteryItem.from_fields({'price_opt': 100, 'price_recommended': 100}),
        BatteryItem.from_fields({'price_opt': 100, 'price_recommended': '115.17'}),
    ]
    stats = BatteryResultStatistic(positions)
    assert stats.real_absolute_markup() == (-9.9, 15.2)
    assert stats.real_percents_markup() == (-9.9, 15.2)
