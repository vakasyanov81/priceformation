"""В отчёт попадают только размеченные группы с несколькими предложениями."""

from dataclasses import replace

from domain.battery.duplicate import BatteryDuplicate
from domain.battery.item import BatteryItem
from parsers.battery.doubles import double_positions


def test_only_repeated_groups_keep_main_offer_first() -> None:
    position = BatteryItem.from_fields({'title': 'АКБ', 'price_recommended': '5000'})
    positions = tuple(
        replace(position, duplicate=mark)
        for mark in (
            BatteryDuplicate(1, False),
            BatteryDuplicate(2, True),
            BatteryDuplicate(),
            BatteryDuplicate(1, True),
            BatteryDuplicate(),
        )
    )
    assert double_positions(positions) == (positions[3], positions[0])
    assert positions[0].duplicate.is_main is False
    assert positions[0].offer.sale_price == position.offer.sale_price


def test_empty_package_has_no_doubles() -> None:
    assert double_positions(()) == ()
