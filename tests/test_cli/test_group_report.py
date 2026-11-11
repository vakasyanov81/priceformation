"""Контракт v2 с независимой тестовой моделью без шинных полей."""

import json
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.parse_report import REPORT_VERSION
from app.parse_report_build import report_from_result
from app.parse_report_groups import positions_to_json
from app.run_machine import machine_json
from domain.product_group_result import ProductGroupResult, ProductPosition, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from services.parse_orchestrator import ParseOrchestrator
from services.parse_result import ParseResult, ParseSelection
from services.parse_statistics import GroupStatistics
from services.price_report import PriceReportService


@dataclass(frozen=True)
class _OtherPosition:
    label: str
    product_group = ProductGroup.BATTERIES


@dataclass(frozen=True)
class _OtherPackage:
    positions: tuple[_OtherPosition, ...]
    product_group = ProductGroup.BATTERIES

    def merge(self, _other: ProductGroupResult[ProductPosition]) -> ProductGroupResult[ProductPosition]:
        raise NotImplementedError


@positions_to_json.register
def _other_positions(package: _OtherPackage) -> list[dict[str, Any]]:
    return [{'label': position.label} for position in package.positions]


@pytest.mark.parametrize('all_result', [False, True])
def test_two_models_report(all_result: bool) -> None:
    """Схемы позиций различны; суммируются только общие счётчики выбранных групп."""
    parsed = ParseResult(unrouted_rows=7)
    parsed.add_package(TireAndDiskResult((RowItem({'title': 'шина'}),)))
    parsed.add_package(_OtherPackage((_OtherPosition('пример'),)))
    parsed.statistics = {
        ProductGroup.TIRE_AND_DISK: GroupStatistics(priced_items=1, doubles=1, black_list_skips=2),
        ProductGroup.BATTERIES: GroupStatistics(priced_items=1, black_list_skips=3),
    }
    report = report_from_result('parse', parsed, [], 1, all_result=all_result)
    assert report['version'] == 2
    assert 'positions' not in report
    expected_positions = [{'label': 'пример'}] if all_result else []
    assert report['groups']['batteries'] == {
        'positions': expected_positions,
        'stats': {'items': 1, 'priced_items': 1, 'doubles': 0, 'black_list_skips': 3},
    }
    assert report['stats'] == {
        'items': 2,
        'priced_items': 2,
        'doubles': 1,
        'black_list_skips': 5,
        'unrouted_rows': 7,
        'elapsed_seconds': 1,
    }
    assert 'percent_markup' in report['groups']['tire_and_disk']['stats']


def test_selected_empty_group_and_absent_group() -> None:
    """Пустой выбор отличается от выбранной группы с нулём позиций."""
    parsed = ParseResult()
    assert report_from_result('parse', parsed, [], 0)['groups'] == {}
    parsed.add_package(TireAndDiskResult())
    report = report_from_result('parse', parsed, [], 0, all_result=True)
    assert set(report['groups']) == {'tire_and_disk'}
    assert report['groups']['tire_and_disk']['positions'] == []
    assert report['groups']['tire_and_disk']['stats']['items'] == 0


def test_missing_model_serializer_rejected() -> None:
    """Неизвестная модель не превращается в шинную строку или строковое представление."""
    with pytest.raises(TypeError, match='JSON-преобразователя'):
        positions_to_json(object())


def test_empty_parse_creates_no_files(capsys: pytest.CaptureFixture[str]) -> None:
    """Без выбранных групп писатель не запускается и метаданные не появляются."""
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = ParseResult()
    reporter = MagicMock()
    with patch(
        'app.run_machine.ServiceProvider.resolve',
        side_effect={
            ParseOrchestrator: orchestrator,
            PriceReportService: reporter,
        }.__getitem__,
    ):
        assert machine_json('parse') == 0
    report = json.loads(capsys.readouterr().out)
    assert report['version'] == 2
    assert report['groups'] == {}
    assert report['files'] == []
    reporter.write_prices.assert_not_called()


@pytest.mark.parametrize('during_write', [False, True])
def test_known_selection_on_failure(during_write: bool, capsys: pytest.CaptureFixture[str]) -> None:
    """Ошибка чтения или записи не публикует частичные позиции и пути."""
    parsed = ParseResult()
    parsed.add_package(TireAndDiskResult((RowItem({'title': 'частичный результат'}),)))

    def parse_all(*, selection: ParseSelection) -> ParseResult:
        selection.groups = (ProductGroup.TIRE_AND_DISK,)
        if not during_write:
            raise ValueError('ошибка чтения')
        return parsed

    orchestrator = MagicMock()
    orchestrator.parse_all.side_effect = parse_all
    reporter = MagicMock()
    reporter.write_prices.side_effect = ValueError('ошибка записи')
    with patch(
        'app.run_machine.ServiceProvider.resolve',
        side_effect={
            ParseOrchestrator: orchestrator,
            PriceReportService: reporter,
        }.__getitem__,
    ):
        assert machine_json('parse', all_result=True) == 1
    report = json.loads(capsys.readouterr().out)
    assert report['version'] == REPORT_VERSION == 2
    assert report['ok'] is False
    assert report['files'] == []
    assert report['groups']['tire_and_disk']['positions'] == []
    assert report['stats']['items'] == 0
