"""Выгрузка по API учитывает флаг enabled поставщика."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.logging.console import FILE_ONLY
from parsers.vendor_config.models import VendorConfig
from services.four_tochki_service import FourTochkiService
from services.mim_service import MimService
from services.vendor_activity import is_vendor_enabled
from services.zapaska_service import ZapaskaService

_API = MagicMock()


def _configs(folder: str, *, enabled: bool) -> dict[str, VendorConfig]:
    return {folder: MagicMock(spec=VendorConfig, enabled=enabled)}


_CASES = [
    ({}, True),
    (_configs('zapaska', enabled=True), True),
    (_configs('zapaska', enabled=False), False),
]


@pytest.mark.parametrize(('configs', 'expected'), _CASES)
def test_is_vendor_enabled(configs: dict[str, VendorConfig], expected: bool) -> None:
    with patch('services.vendor_activity.load_vendor_configs', return_value=configs):
        assert is_vendor_enabled('zapaska', MagicMock()) is expected


def test_zapaska_disabled_not_loaded(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger='services.vendor_activity')
    with (
        patch('services.vendor_activity.load_vendor_configs', return_value=_configs('zapaska', enabled=False)),
        patch('services.zapaska_service.get_zapaska_api_config') as api,
        patch('services.zapaska_service.load_remote_vendor_data') as load,
    ):
        assert ZapaskaService().upload_data() is False
    api.assert_not_called()
    load.assert_not_called()
    record = next(record for record in caplog.records if record.name == 'services.vendor_activity')
    assert getattr(record, FILE_ONLY, False) is True


def test_four_tochki_disabled_not_loaded() -> None:
    with (
        patch('services.vendor_activity.load_vendor_configs', return_value=_configs('four_tochki', enabled=False)),
        patch('services.four_tochki_service.load_remote_vendor_data') as load,
    ):
        assert FourTochkiService().upload_data() is False
    load.assert_not_called()


def test_mim_disabled_not_loaded() -> None:
    configs = _configs('mim', enabled=False)
    with (
        patch('services.vendor_activity.load_vendor_configs', return_value=configs),
        patch('services.mim_service.get_mim_api_config', return_value=_API),
        patch('services.mim_service.load_remote_vendor_data') as load,
    ):
        assert MimService().upload_data() is False
    load.assert_not_called()
