"""Обработчик меню: получение прайсов поставщиков из почты."""

import logging
from unittest.mock import MagicMock, patch

from log_watch import LoggerWatcher, texts_at

from run_dialog import AnswerResult
from services.mail_service import MailService

_ASK_ACTION = 'run.ask_action'
_RUN_LOGGER = 'run'


def test_response_fetch_mail() -> None:
    """действие получения прайсов из почты вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.FETCH_MAIL_PRICES),
        patch('run.try_call') as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == 'run_fetch_mail_prices'


def test_run_fetch_mail_prices(watch_logger: LoggerWatcher) -> None:
    """выгрузка прайсов из почты через сервис и сообщение о количестве файлов"""
    mail_service = MagicMock()
    mail_service.fetch_prices.return_value = [MagicMock(), MagicMock()]
    entries = watch_logger(_RUN_LOGGER)

    with patch(
        'run.ServiceProvider.resolve',
        side_effect={MailService: mail_service}.__getitem__,
    ):
        from run import run_fetch_mail_prices

        run_fetch_mail_prices()

    mail_service.fetch_prices.assert_called_once_with()
    assert texts_at(entries(), logging.INFO) == ['*** Прайсы из почты получены: 2. ***\n']


def test_response_update_all_supplier_prices() -> None:
    """пункт «обновить прайсы всех поставщиков» вызывает try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.UPDATE_ALL_SUPPLIER_PRICES),
        patch('run.try_call') as mock_try,
    ):
        from run import response_processing

        assert response_processing() is True
        assert mock_try.call_args.args[0].__name__ == 'run_update_all_supplier_prices'


def test_run_update_all_prices_order() -> None:
    """запаска, Форточки и почта вызываются по порядку, каждый через try_call"""
    calls = MagicMock()
    with (
        patch('run.run_upload_zapaska_data', calls.zapaska),
        patch('run.run_upload_four_tochki_data', calls.four_tochki),
        patch('run.run_fetch_mail_prices', calls.mail),
    ):
        from run import run_update_all_supplier_prices

        run_update_all_supplier_prices()
        assert [call[0] for call in calls.mock_calls] == ['zapaska', 'four_tochki', 'mail']
