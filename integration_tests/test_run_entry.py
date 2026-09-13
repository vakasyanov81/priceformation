"""Integration tests for application entry point (src/run.py)."""

from unittest.mock import MagicMock, patch

import pytest

from core.exceptions import SupplierNotHavePricesError
from run_dialog import AnswerResult
from services.doubles_service import DoublesService
from services.parse_orchestrator import ParseOrchestrator
from services.price_report import PriceReportService
from services.zapaska_service import ZapaskaService

_INPUT = 'builtins.input'
_RUN_EXIT = 'run.sys.exit'
_QUIT = 'q'
_PARSED_ROW = 'item'
_RESOLVE = 'run.ServiceProvider.resolve'
_REPORT_PATH = 'file_prices/result/doubles.xlsx'


def test_main_exits_on_quit() -> None:
    """main завершает процесс при выборе выхода из меню."""
    with (
        patch(_INPUT, return_value=_QUIT),
        patch(_RUN_EXIT, side_effect=SystemExit(0)) as mock_exit,
        patch('run.init_cfg') as mock_init,
    ):
        from run import main

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 0
        mock_exit.assert_called_with(0)
        mock_init.assert_called_once()


def test_main_make_price_then_exit() -> None:
    """выбор 1 вызывает полный путь формирования прайса, затем выход."""
    parsed = MagicMock()
    parsed.parsed_items = [_PARSED_ROW]
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = MagicMock()

    with (
        patch(_INPUT, side_effect=['1', _QUIT]),
        patch(
            _RESOLVE,
            side_effect={ParseOrchestrator: orchestrator, PriceReportService: reporter}.__getitem__,
        ),
        patch(_RUN_EXIT, side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        orchestrator.parse_all.assert_called_once()
        reporter.write_prices.assert_called_once_with([_PARSED_ROW], template=None)


def test_main_report_doubles_then_exit() -> None:
    """выбор 3 вызывает отчёт о дублях, затем выход."""
    report = MagicMock()
    report.path = _REPORT_PATH
    doubles_service = MagicMock()
    doubles_service.make_report.return_value = report

    with (
        patch(_INPUT, side_effect=['3', _QUIT]),
        patch(_RESOLVE, side_effect={DoublesService: doubles_service}.__getitem__),
        patch('run.print_log'),
        patch(_RUN_EXIT, side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        doubles_service.make_report.assert_called_once()


def test_main_update_zapaska_then_exit() -> None:
    """выбор 2 вызывает загрузку данных запаски через try_call, затем выход."""
    zapaska_service = MagicMock()
    with (
        patch(_INPUT, side_effect=['2', _QUIT]),
        patch(_RESOLVE, side_effect={ZapaskaService: zapaska_service}.__getitem__),
        patch('run.print_log') as mock_log,
        patch(_RUN_EXIT, side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        zapaska_service.upload_data.assert_called_once()
        mock_log.assert_called_once()


def test_main_retries_invalid_menu_input() -> None:
    """неверный ввод меню игнорируется, затем выполняется валидное действие."""
    with (
        patch(_INPUT, side_effect=['x', _QUIT]),
        patch('run.print_log'),
        patch('run_dialog.print_log') as mock_dialog_log,
        patch(_RUN_EXIT, side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_dialog_log.assert_called_once()


def test_response_make_price_via_try_call() -> None:
    """response_processing проходит через try_call до run_make_price_by_supplier."""
    parsed = MagicMock()
    parsed.parsed_items = []
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = MagicMock()

    with (
        patch('run.ask_action', return_value=AnswerResult.MAKE_PRICE_BY_SUPPLIER),
        patch(
            _RESOLVE,
            side_effect={ParseOrchestrator: orchestrator, PriceReportService: reporter}.__getitem__,
        ),
    ):
        from run import response_processing

        assert response_processing() is True

        orchestrator.parse_all.assert_called_once()
        reporter.write_prices.assert_called_once_with([], template=None)


def test_response_supplier_error_exits() -> None:
    """SupplierNotHavePricesError в try_call завершает процесс с кодом 1."""
    with (
        patch('run.ask_action', return_value=AnswerResult.MAKE_PRICE_BY_SUPPLIER),
        patch('run.run_make_price_by_supplier', side_effect=SupplierNotHavePricesError('empty')),
        patch('core.async_utils.print_log'),
        patch('core.async_utils.sys.exit', side_effect=SystemExit(1)) as mock_exit,
    ):
        from run import response_processing

        with pytest.raises(SystemExit) as exit_info:
            response_processing()

        assert exit_info.value.code == 1
        mock_exit.assert_called_once_with(1)
