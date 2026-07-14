"""Integration tests for application entry point (src/run.py)."""

# pylint: disable=import-outside-toplevel

from unittest.mock import MagicMock, patch

import pytest

from core.exceptions import SupplierNotHavePricesError
from run_dialog import AnswerResult

_INPUT = "builtins.input"
_RUN_EXIT = "run.sys.exit"
_QUIT = "q"


def test_main_exits_on_quit():
    """main завершает процесс при выборе выхода из меню."""
    with (
        patch(_INPUT, return_value=_QUIT),
        patch(_RUN_EXIT, side_effect=SystemExit(0)) as mock_exit,
    ):
        from run import main

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 0
        mock_exit.assert_called_with(0)


def test_main_make_price_then_exit():
    """выбор 1 вызывает полный путь формирования прайса, затем выход."""
    common = MagicMock()
    common.result = ["item"]

    with (
        patch(_INPUT, side_effect=["1", _QUIT]),
        patch("run.CommonPrice", return_value=common) as mock_cp,
        patch("run.all_vendors", return_value=[("vendor", None)]),
        patch("run.CommonPriceOut") as mock_out,
        patch(_RUN_EXIT, side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_cp.assert_called_once()
        common.parse_all_vendors.assert_called_once_with([("vendor", None)])
        mock_out.assert_called_once_with(["item"])
        mock_out.return_value.write_all_prices.assert_called_once()


def test_main_update_zapaska_then_exit():
    """выбор 2 вызывает загрузку данных запаски через try_call, затем выход."""
    with (
        patch(_INPUT, side_effect=["2", _QUIT]),
        patch("run.load_data") as mock_load,
        patch("run.print_log") as mock_log,
        patch(_RUN_EXIT, side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_load.assert_called_once()
        mock_log.assert_called_once()


def test_main_retries_invalid_menu_input():
    """неверный ввод меню игнорируется, затем выполняется валидное действие."""
    with (
        patch(_INPUT, side_effect=["x", _QUIT]),
        patch("run.print_log"),
        patch("run_dialog.print_log") as mock_dialog_log,
        patch(_RUN_EXIT, side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_dialog_log.assert_called_once()


def test_response_make_price_via_try_call():
    """response_processing проходит через try_call до run_make_price_by_supplier."""
    common = MagicMock()
    common.result = []

    with (
        patch("run.ask_action", return_value=AnswerResult.MAKE_PRICE_BY_SUPPLIER),
        patch("run.CommonPrice", return_value=common),
        patch("run.all_vendors", return_value=[]),
        patch("run.CommonPriceOut") as mock_out,
    ):
        from run import response_processing

        response_processing()

        common.parse_all_vendors.assert_called_once_with([])
        mock_out.return_value.write_all_prices.assert_called_once()


def test_response_supplier_error_exits():
    """SupplierNotHavePricesError в try_call завершает процесс с кодом 1."""
    with (
        patch("run.ask_action", return_value=AnswerResult.MAKE_PRICE_BY_SUPPLIER),
        patch("run.run_make_price_by_supplier", side_effect=SupplierNotHavePricesError("empty")),
        patch("core.async_utils.print_log"),
        patch("core.async_utils.sys.exit", side_effect=SystemExit(1)) as mock_exit,
    ):
        from run import response_processing

        with pytest.raises(SystemExit) as exit_info:
            response_processing()

        assert exit_info.value.code == 1
        mock_exit.assert_called_once_with(1)
