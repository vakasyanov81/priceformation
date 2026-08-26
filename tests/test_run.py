"""tests for CLI entrypoint handlers"""

from unittest.mock import MagicMock, patch

from run_dialog import AnswerResult

_ASK_ACTION = "run.ask_action"
_VENDOR = "v"
_REPORT_PATH = "file_prices/result/doubles.xlsx"


def test_response_make_price() -> None:
    """действие формирования прайса вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.MAKE_PRICE_BY_SUPPLIER),
        patch("run.try_call") as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == "run_make_price_by_supplier"


def test_response_update_zapaska() -> None:
    """действие выгрузки запаски вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.UPDATE_ZAPASKA_DATA),
        patch("run.try_call") as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == "run_upload_zapaska_data"


def test_response_report_doubles() -> None:
    """действие отчёта о дублях вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.REPORT_DOUBLES),
        patch("run.try_call") as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == "run_report_doubles"


def test_response_exit() -> None:
    """выход останавливает цикл; sys.exit вызывает main."""
    with patch(_ASK_ACTION, return_value=AnswerResult.EXIT):
        from run import response_processing

        assert response_processing() is False


def test_run_make_price() -> None:
    """сборка общего прайса и запись"""
    common = MagicMock()
    common.parsed_items = [1]

    with (
        patch("run.CommonPrice", return_value=common) as mock_cp,
        patch("run.all_vendors", return_value=[(_VENDOR, None)]),
        patch("run.CommonPriceOut") as mock_out,
    ):
        from run import run_make_price_by_supplier

        run_make_price_by_supplier()
        mock_cp.assert_called_once()
        common.parse_all_vendors.assert_called_once_with([(_VENDOR, None)])
        mock_out.assert_called_once_with([1])
        mock_out.return_value.write_all_prices.assert_called_once()


def test_run_upload_zapaska() -> None:
    """загрузка данных запаски и сообщение об успехе"""
    api = MagicMock()
    with (
        patch("run.get_zapaska_api_config", return_value=api),
        patch("run.load_remote_vendor_data") as mock_load,
        patch("run.print_log") as mock_log,
    ):
        from run import run_upload_zapaska_data

        run_upload_zapaska_data()
        mock_load.assert_called_once_with(api=api)
        mock_log.assert_called_once()


def test_run_report_doubles() -> None:
    """разбор прайсов и запись отчёта о дублях"""
    common = MagicMock()
    common.parsed_items = [1]

    with (
        patch("run.CommonPrice", return_value=common) as mock_cp,
        patch("run.all_vendors", return_value=[(_VENDOR, None)]),
        patch("run.CommonPriceOut") as mock_out,
        patch("run.print_log") as mock_log,
    ):
        from run import run_report_doubles

        mock_out.return_value.write_doubles_report.return_value = _REPORT_PATH
        run_report_doubles()
        mock_cp.assert_called_once()
        common.parse_all_vendors.assert_called_once_with([(_VENDOR, None)])
        mock_out.assert_called_once_with([1])
        mock_out.return_value.write_doubles_report.assert_called_once()
        mock_log.assert_called_once()
        assert _REPORT_PATH in mock_log.call_args.args[0]
