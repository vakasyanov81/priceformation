"""Пункт меню и загрузка данных МИМ по API (run.py)."""

import logging
from unittest.mock import MagicMock, patch

from log_watch import LoggerWatcher, texts_at

from run_dialog import AnswerResult
from services.mim_service import MimService
from services.price_schema_service import PriceSchemaService

_ASK_ACTION = 'run.ask_action'
_RUN_LOGGER = 'run'


def test_response_update_mim() -> None:
    """действие выгрузки МИМ вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.UPDATE_MIM_DATA),
        patch('run.try_call') as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        assert mock_try.call_args.args[0].__name__ == 'run_upload_mim_data'


def test_run_upload_mim(watch_logger: LoggerWatcher) -> None:
    """загрузка данных МИМ через сервис и сообщение об успехе"""
    mim_service = MagicMock()
    entries = watch_logger(_RUN_LOGGER)
    with patch(
        'run.ServiceProvider.resolve',
        side_effect={MimService: mim_service, PriceSchemaService: MagicMock()}.__getitem__,
    ):
        from run import run_upload_mim_data

        run_upload_mim_data()

    mim_service.upload_data.assert_called_once_with()
    assert texts_at(entries(), logging.INFO) == ['*** Данные МИМ успешно загружены. ***\n']
