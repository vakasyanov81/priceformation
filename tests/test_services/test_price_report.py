"""Контракты сборки писателей и проверки зависимостей сервиса отчётов."""

from unittest.mock import MagicMock, patch

import pytest

from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from services.parse_result import ParseResult
from services.price_report import PriceReportService


@pytest.mark.parametrize('missing_writer', [False, True])
def test_write_result_requires_both_dependencies(missing_writer: bool) -> None:
    """Отсутствие любой из двух зависимостей отклоняется до подготовки источников."""
    service = PriceReportService(
        writer_factory=MagicMock(),
        group_writer_factory=None if missing_writer else MagicMock(),
        config_provider=MagicMock() if missing_writer else None,
    )

    with pytest.raises(RuntimeError, match=r'^Фабрика групповой записи не настроена$'):
        service.write_result(ParseResult())


def test_from_factories_passes_nonempty_positions(fake_config_provider: FakeConfigProvider) -> None:
    """Фабрика старого писателя сохраняет переданные позиции и зависимости."""
    rows = [RowItem({'title': 'Позиция'})]
    xls_writer = MagicMock()
    driver = MagicMock()
    service = PriceReportService.from_factories(
        xls_writer=xls_writer, write_driver=driver, config_provider=lambda: fake_config_provider
    )

    with patch('services.price_report.CommonPriceOut') as output:
        service.write_prices(rows)

    output.assert_called_once_with(
        rows, xls_writer=xls_writer, write_driver=driver, config_provider=fake_config_provider
    )


def test_from_factories_connects_group_writer(fake_config_provider: FakeConfigProvider) -> None:
    """Групповая запись получает фабрики и актуальные пути переданного провайдера."""
    xls_writer = MagicMock()
    driver = MagicMock()
    service = PriceReportService.from_factories(
        xls_writer=xls_writer, write_driver=driver, config_provider=lambda: fake_config_provider
    )
    parsed = ParseResult()
    with (
        patch('services.price_report.GroupFileWriter') as writer,
        patch('services.price_report.output_sources', return_value={}) as sources,
        patch('services.price_report.write_group_prices', return_value=[]) as write,
    ):
        assert service.write_result(parsed) == []

    writer.assert_called_once_with(
        xls_writer=xls_writer, write_driver=driver, result_folder=fake_config_provider.result_folder()
    )
    sources.assert_called_once_with(parsed.groups, fake_config_provider)
    selected = parsed.groups.keys()
    write.assert_called_once_with(writer.return_value, {}, template=None, as_jsonl=False, selected=selected)
