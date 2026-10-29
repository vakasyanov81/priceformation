"""Пункт меню и загрузка данных Форточек по API (app.run.py)."""

import logging
from unittest.mock import MagicMock, patch

from log_watch import LoggerWatcher, texts_at

from services.price_schema_service import PriceSchemaService

_ASK_ACTION = 'app.run.ask_action'
_RUN_LOGGER = 'app.run'


def test_run_upload_four_tochki(watch_logger: LoggerWatcher) -> None:
    """загрузка данных Форточек через сервис и сообщение об успехе"""
    entries = watch_logger(_RUN_LOGGER)
    upload = MagicMock()
    with (
        patch('app.run.upload_four_tochki_data', upload),
        patch('app.run.ServiceProvider.resolve', side_effect={PriceSchemaService: MagicMock()}.__getitem__),
    ):
        from app.run import run_upload_four_tochki_data

        run_upload_four_tochki_data()

    upload.assert_called_once_with()
    assert texts_at(entries(), logging.INFO) == ['*** Данные Форточек успешно загружены. ***\n']
