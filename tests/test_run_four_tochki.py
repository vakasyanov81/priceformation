"""Пункт меню и загрузка данных Форточек по API (run.py)."""

import logging
from unittest.mock import MagicMock, patch

from log_watch import LoggerWatcher, texts_at

from run_dialog import AnswerResult

_ASK_ACTION = 'run.ask_action'
_RUN_LOGGER = 'run'


def test_response_four_tochki() -> None:
    """действие выгрузки Форточек вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.UPDATE_FOUR_TOCHKI_DATA),
        patch('run.try_call') as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == 'run_upload_four_tochki_data'


def test_run_upload_four_tochki(watch_logger: LoggerWatcher) -> None:
    """загрузка данных Форточек через сервис и сообщение об успехе"""
    entries = watch_logger(_RUN_LOGGER)
    upload = MagicMock()
    with patch('run.upload_four_tochki_data', upload):
        from run import run_upload_four_tochki_data

        run_upload_four_tochki_data()

    upload.assert_called_once_with()
    assert texts_at(entries(), logging.INFO) == ['*** Данные Форточек успешно загружены. ***\n']
