"""tests for CLI entrypoint handlers"""

# pylint: disable=import-outside-toplevel

from unittest.mock import MagicMock, patch

from run_dialog import AnswerResult


def test_response_make_price():
    """действие формирования прайса вызывает try_call"""
    with (
        patch("run.ask_action", return_value=AnswerResult.MAKE_PRICE_BY_SUPPLIER),
        patch("run.try_call") as mock_try,
    ):
        from run import response_processing

        response_processing()
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == "run_make_price_by_supplier"


def test_response_update_zapaska():
    """действие выгрузки запаски вызывает try_call"""
    with (
        patch("run.ask_action", return_value=AnswerResult.UPDATE_ZAPASKA_DATA),
        patch("run.try_call") as mock_try,
    ):
        from run import response_processing

        response_processing()
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == "run_upload_zapaska_data"


def test_response_exit():
    """выход завершает процесс"""
    with (
        patch("run.ask_action", return_value=AnswerResult.EXIT),
        patch("run.sys.exit") as mock_exit,
    ):
        from run import response_processing

        response_processing()
        mock_exit.assert_called_once_with(0)


def test_run_make_price():
    """сборка общего прайса и запись"""
    common = MagicMock()
    common.result = [1]

    with (
        patch("run.CommonPrice", return_value=common) as mock_cp,
        patch("run.all_vendors", return_value=[("v", None)]),
        patch("run.CommonPriceOut") as mock_out,
    ):
        from run import run_make_price_by_supplier

        run_make_price_by_supplier()
        mock_cp.assert_called_once()
        common.parse_all_vendors.assert_called_once_with([("v", None)])
        mock_out.assert_called_once_with([1])
        mock_out.return_value.write_all_prices.assert_called_once()


def test_run_upload_zapaska():
    """загрузка данных запаски и сообщение об успехе"""
    with (
        patch("run.load_data") as mock_load,
        patch("run.print_log") as mock_log,
    ):
        from run import run_upload_zapaska_data

        run_upload_zapaska_data()
        mock_load.assert_called_once()
        mock_log.assert_called_once()
