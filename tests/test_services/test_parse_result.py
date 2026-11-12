"""Контракт результата разбора, составленного из пакетов товарных групп."""

import pytest

from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.base_parser.parse_statistic import ParserStats
from services.parse_result import ParseResult
from services.parse_statistics import GroupStatistics, TireAndDiskDiagnostics
from tests.test_domain.group_handler_examples import TestGroupResult, TestPosition


def test_absent_group_is_not_replaced_with_empty_package() -> None:
    """Невыбранная группа отсутствует, а не создаётся при обращении из старого writer."""
    parsed = ParseResult()

    assert parsed.groups == {}
    assert parsed.tire_and_disk_items == []
    assert parsed.groups == {}


def test_selected_empty_group_keeps_its_identity() -> None:
    """Выбранная группа с нулём позиций присутствует собственным пустым пакетом."""
    parsed = ParseResult()

    parsed.add_package(TireAndDiskResult())

    assert set(parsed.groups) == {ProductGroup.TIRE_AND_DISK}
    assert parsed.groups[ProductGroup.TIRE_AND_DISK].positions == ()


def test_packages_from_suppliers_merge_without_mutating_originals() -> None:
    """Позиции поставщиков одной группы объединяются в новый неизменяемый пакет."""
    first_row = RowItem({'title': 'Первая'})
    second_row = RowItem({'title': 'Вторая'})
    first = TireAndDiskResult((first_row,))
    second = TireAndDiskResult((second_row,))
    parsed = ParseResult()

    parsed.add_package(first)
    parsed.add_package(second)

    assert first.positions == (first_row,)
    assert second.positions == (second_row,)
    assert parsed.tire_and_disk_items == [first_row, second_row]


def test_different_group_models_remain_separate() -> None:
    """Общий контейнер объединяет пакеты, но не смешивает позиции разных моделей."""
    tire = RowItem({'title': 'Шина'})
    other = TestPosition('Другая модель')
    parsed = ParseResult()

    parsed.add_package(TireAndDiskResult((tire,)))
    parsed.add_package(TestGroupResult((other,)))

    assert parsed.tire_and_disk_items == [tire]
    assert parsed.groups[ProductGroup.BATTERIES].positions == (other,)


def test_package_rejects_merge_with_another_model() -> None:
    """Нетипизированный код не может объединить несовместимые доменные модели."""
    with pytest.raises(TypeError, match='той же моделью'):
        TireAndDiskResult().merge(TestGroupResult(()))


def test_common_statistics_sum_selected_packages_only() -> None:
    """Итоги двух моделей не читают шинные поля чужих позиций или невыбранные группы."""
    parsed = ParseResult()
    parsed.add_package(TireAndDiskResult((RowItem(),)))
    parsed.add_package(TestGroupResult((TestPosition('Другая модель'),)))
    parsed.statistics = {
        ProductGroup.TIRE_AND_DISK: GroupStatistics(priced_items=1, doubles=1, black_list_skips=2),
        ProductGroup.BATTERIES: GroupStatistics(black_list_skips=3),
    }

    expected = GroupStatistics(item_count=2, priced_items=1, doubles=1, black_list_skips=5)
    assert parsed.total_statistics() == expected
    assert not hasattr(parsed.statistics[ProductGroup.BATTERIES], 'type_corrections')
    assert not hasattr(parsed.statistics[ProductGroup.BATTERIES], 'unknown_category_skips')
    parsed.groups.pop(ProductGroup.BATTERIES)
    assert parsed.total_statistics().black_list_skips == 2


def test_diagnostics_accumulate_without_sharing_parser_state() -> None:
    """Сброс счётчиков парсера после секции не меняет уже собранную диагностику."""
    counters = ParserStats(type_corrections=2, title_conflicts=1, homoglyph_fixes=3, homoglyph_suspects=4)
    skips = [('Поставщик / секция', 'SUV')]
    diagnostics = TireAndDiskDiagnostics()

    diagnostics.accumulate(counters, skips)
    diagnostics.accumulate(counters, skips)
    counters.type_corrections = 0
    skips.clear()

    assert diagnostics.type_corrections == 4
    assert diagnostics.title_conflicts == 2
    assert diagnostics.homoglyph_fixes == 6
    assert diagnostics.homoglyph_suspects == 8
    assert diagnostics.unknown_category_skips == [('Поставщик / секция', 'SUV'), ('Поставщик / секция', 'SUV')]
