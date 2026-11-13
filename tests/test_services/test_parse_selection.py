"""Выбор групп известен до сборки парсеров и чтения прайсов."""

from unittest.mock import MagicMock

import pytest

from domain.product_groups import ProductGroup
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from services.parse_orchestrator import ParseOrchestrator
from services.parse_result import ParseSelection


def test_selection_available_before_parser_failure() -> None:
    """Сбой сборки не стирает уже определённый выбор, повтор группы не дублируется."""
    selection = ParseSelection()
    factory = MagicMock(side_effect=ValueError('стратегия'))
    orchestrator = ParseOrchestrator(
        parser_factory=factory,
        grouper_factory=MagicMock(),
        vendor_source=MagicMock(),
    )
    with pytest.raises(ValueError, match='стратегия'):
        orchestrator.parse_all([(BaseParser, None), (BaseParser, None)], selection=selection)
    assert selection.groups == (ProductGroup.TIRE_AND_DISK,)


def test_selection_reset_before_vendor_source_failure() -> None:
    """Ранний отказ загрузчика не возвращает выбор предыдущего запуска."""
    selection = ParseSelection((ProductGroup.TIRE_AND_DISK,))
    source = MagicMock()
    source.all.side_effect = ValueError('конфиг')
    orchestrator = ParseOrchestrator(
        parser_factory=MagicMock(),
        grouper_factory=MagicMock(),
        vendor_source=source,
    )
    with pytest.raises(ValueError, match='конфиг'):
        orchestrator.parse_all(selection=selection)
    assert selection.groups == ()


def test_battery_selection_available_before_parser_failure() -> None:
    """Ошибка сборки АКБ сохраняет аккумуляторную группу вместо шинной по умолчанию."""
    selection = ParseSelection()
    config = MagicMock(spec=ParseConfiguration, product_group=ProductGroup.BATTERIES)
    orchestrator = ParseOrchestrator(
        parser_factory=MagicMock(side_effect=ValueError('стратегия')),
        grouper_factory=MagicMock(),
        vendor_source=MagicMock(),
    )

    with pytest.raises(ValueError, match='стратегия'):
        orchestrator.parse_all([(BaseParser, config)], selection=selection)

    assert selection.groups == (ProductGroup.BATTERIES,)
