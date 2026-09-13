"""tests for CLI entrypoint handlers"""

from unittest.mock import MagicMock, patch

from run_dialog import AnswerResult
from services.doubles_service import DoublesService
from services.parse_orchestrator import ParseOrchestrator
from services.price_report import PriceReportService
from services.zapaska_service import ZapaskaService

_ASK_ACTION = 'run.ask_action'
_REPORT_PATH = 'file_prices/result/doubles.xlsx'


def test_response_make_price() -> None:
    """действие формирования прайса вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.MAKE_PRICE_BY_SUPPLIER),
        patch('run.try_call') as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == 'run_make_price_by_supplier'


def test_response_update_zapaska() -> None:
    """действие выгрузки запаски вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.UPDATE_ZAPASKA_DATA),
        patch('run.try_call') as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == 'run_upload_zapaska_data'


def test_response_report_doubles() -> None:
    """действие отчёта о дублях вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.REPORT_DOUBLES),
        patch('run.try_call') as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == 'run_report_doubles'


def test_response_exit() -> None:
    """выход останавливает цикл; sys.exit вызывает main."""
    with patch(_ASK_ACTION, return_value=AnswerResult.EXIT):
        from run import response_processing

        assert response_processing() is False


def test_run_make_price() -> None:
    """сборка общего прайса и запись через сервисы"""
    parsed = MagicMock()
    parsed.parsed_items = [1]
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = MagicMock()

    with patch(
        'run.ServiceProvider.resolve',
        side_effect={ParseOrchestrator: orchestrator, PriceReportService: reporter}.__getitem__,
    ):
        from run import run_make_price_by_supplier

        run_make_price_by_supplier()
        orchestrator.parse_all.assert_called_once()
        reporter.write_prices.assert_called_once_with([1], template=None)
        run_make_price_by_supplier(result_template='for_drom')
        reporter.write_prices.assert_called_with([1], template='for_drom')


def test_run_upload_zapaska() -> None:
    """загрузка данных запаски через сервис и сообщение об успехе"""
    zapaska_service = MagicMock()
    with (
        patch(
            'run.ServiceProvider.resolve',
            side_effect={ZapaskaService: zapaska_service}.__getitem__,
        ),
        patch('run.print_log') as mock_log,
    ):
        from run import run_upload_zapaska_data

        run_upload_zapaska_data()
        zapaska_service.upload_data.assert_called_once_with()
        mock_log.assert_called_once()


def test_run_report_doubles() -> None:
    """разбор прайсов и запись отчёта о дублях через сервис"""
    report = MagicMock()
    report.path = _REPORT_PATH
    doubles_service = MagicMock()
    doubles_service.make_report.return_value = report

    with (
        patch(
            'run.ServiceProvider.resolve',
            side_effect={DoublesService: doubles_service}.__getitem__,
        ),
        patch('run.print_log') as mock_log,
    ):
        from run import run_report_doubles

        run_report_doubles()
        doubles_service.make_report.assert_called_once_with()
        mock_log.assert_called_once()
        assert _REPORT_PATH in mock_log.call_args.args[0]
