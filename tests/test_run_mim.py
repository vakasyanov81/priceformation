"""Пункт меню и загрузка данных МИМ по API (app.run.py)."""

import logging
from unittest.mock import MagicMock, patch

from log_watch import LoggerWatcher, texts_at

from services.mim_service import MimService
from services.price_schema_service import PriceSchemaService

_ASK_ACTION = 'app.run.ask_action'
_RUN_LOGGER = 'app.run'


def test_run_upload_mim(watch_logger: LoggerWatcher) -> None:
    """загрузка данных МИМ через сервис и сообщение об успехе"""
    mim_service = MagicMock()
    entries = watch_logger(_RUN_LOGGER)
    with patch(
        'app.run.ServiceProvider.resolve',
        side_effect={MimService: mim_service, PriceSchemaService: MagicMock()}.__getitem__,
    ):
        from app.run import run_upload_mim_data

        run_upload_mim_data()

    mim_service.upload_data.assert_called_once_with()
    assert texts_at(entries(), logging.INFO) == ['*** Данные МИМ успешно загружены. ***\n']
