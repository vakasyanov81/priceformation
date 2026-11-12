"""Тестовые стратегии двух моделей; не регистрируются в приложении."""

from collections.abc import Sequence
from dataclasses import replace

from domain.product_group_result import ProductGroupResult, TireAndDiskResult
from domain.row_item.row_item import RowItem
from parsers.common_price.grouper import CommonPriceGrouper
from tests.test_domain.group_handler_examples import (
    OtherHandlerExample,
    TestGroupResult,
    TestPosition,
    TireHandlerExample,
)


class TireStrategy(TireHandlerExample):
    """Шинная обработка сохраняет предложения и отмечает дубли рабочим группировщиком."""

    def process(self, positions: Sequence[RowItem]) -> TireAndDiskResult:
        for position in positions:
            title = position.identity.title or ''
            position.identity = replace(position.identity, title=title.upper(), model=title)
        return TireAndDiskResult(tuple(positions))

    def group(self, package: ProductGroupResult[RowItem]) -> TireAndDiskResult:
        grouped = CommonPriceGrouper(list(package.positions)).group_by_params().get_row_items()
        return TireAndDiskResult(tuple(grouped))


class OtherStrategy(OtherHandlerExample):
    """Произвольное правило второй модели: нормализация и удаление повторных меток."""

    def process(self, positions: Sequence[TestPosition]) -> TestGroupResult:
        normalized = (TestPosition(position.label.strip().lower()) for position in positions)
        return TestGroupResult(tuple(normalized))

    def group(self, package: ProductGroupResult[TestPosition]) -> TestGroupResult:
        return TestGroupResult(tuple(dict.fromkeys(package.positions)))
