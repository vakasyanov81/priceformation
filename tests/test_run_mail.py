"""Обработчик меню: получение прайсов поставщиков из почты."""

import logging
from unittest.mock import MagicMock, patch

import pytest
from log_watch import LoggerWatcher, texts_at

from domain.exceptions import CoreExceptionError
from run_dialog import AnswerResult
from services.mail_service import MailService
from services.price_schema_service import PriceSchemaService

_ASK_ACTION = 'run.ask_action'
_RUN_LOGGER = 'run'
_RESOLVE = 'run.ServiceProvider.resolve'


def test_run_fetch_mail_prices(watch_logger: LoggerWatcher) -> None:
    """выгрузка прайсов из почты через сервис и сообщение о количестве файлов"""
    mail_service = MagicMock()
    mail_service.fetch_prices.return_value = [MagicMock(), MagicMock()]
    entries = watch_logger(_RUN_LOGGER)

    with patch(
        _RESOLVE,
        side_effect={MailService: mail_service, PriceSchemaService: MagicMock()}.__getitem__,
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
    """запаска, Форточки, МИМ и почта вызываются по порядку, каждый через try_call"""
    calls = MagicMock()
    with (
        patch(_RESOLVE, side_effect={PriceSchemaService: MagicMock()}.__getitem__),
        patch('run.run_upload_zapaska_data', calls.zapaska),
        patch('run.run_upload_four_tochki_data', calls.four_tochki),
        patch('run.run_upload_mim_data', calls.mim),
        patch('run.run_fetch_mail_prices', calls.mail),
    ):
        from run import run_update_all_supplier_prices

        run_update_all_supplier_prices()
        assert [call[0] for call in calls.mock_calls] == ['zapaska', 'four_tochki', 'mim', 'mail']


def test_update_all_single_schema_guard() -> None:
    """сравнение схем — один раз на весь пакет обновлений, а не на каждый источник"""
    schema_service = MagicMock()
    with (
        patch(_RESOLVE, side_effect={PriceSchemaService: schema_service}.__getitem__),
        patch('run.run_upload_zapaska_data'),
        patch('run.run_upload_four_tochki_data'),
        patch('run.run_upload_mim_data'),
        patch('run.run_fetch_mail_prices'),
    ):
        from run import run_update_all_supplier_prices

        run_update_all_supplier_prices()

    schema_service.guard.assert_called_once_with()
    schema_service.guard.return_value.__enter__.assert_called_once_with()


def test_update_all_raises_on_failed_source() -> None:
    """сбой одного источника не отменяет остальные, но итог — ошибка домена, а не тихий успех"""
    mim = MagicMock()

    def run_upload_zapaska_data() -> None:
        raise CoreExceptionError('zapaska down')

    with (
        patch(_RESOLVE, side_effect={PriceSchemaService: MagicMock()}.__getitem__),
        patch('run.run_upload_zapaska_data', run_upload_zapaska_data),
        patch('run.run_upload_four_tochki_data'),
        patch('run.run_upload_mim_data', mim),
        patch('run.run_fetch_mail_prices'),
        patch('services.async_utils.logger'),
    ):
        from run import run_update_all_supplier_prices

        with pytest.raises(CoreExceptionError, match='run_upload_zapaska_data'):
            run_update_all_supplier_prices()
    mim.assert_called_once_with()
