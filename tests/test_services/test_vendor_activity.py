"""Выгрузка по API учитывает флаг enabled поставщика."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domain.config_context import set_config_provider
from infrastructure.config.fake_config_provider import FakeConfigProvider
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


def test_is_vendor_enabled_reads_real_config_from_injected_provider(tmp_path: Path) -> None:
    global_provider = FakeConfigProvider(tmp_path / 'global')
    injected = FakeConfigProvider(tmp_path / 'injected')
    set_config_provider(global_provider)
    for provider, enabled in ((global_provider, True), (injected, False)):
        config = {
            'code': '1',
            'name': 'Запаска',
            'product_groups': [
                {
                    'id': 'tire_and_disk',
                    'start_row': 2,
                    'file_templates': ['price*.xlsx'],
                    'sections': [{'id': '1', 'columns': {'0': 'code', '1': 'title'}}],
                }
            ],
        }
        path = Path(provider.config_file('vendors/zapaska.json'))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config), encoding='utf-8')
        Path(provider.config_file('vendor_activation.json')).write_text(
            json.dumps({'zapaska': int(enabled)}), encoding='utf-8'
        )

    assert is_vendor_enabled('zapaska', global_provider) is True
    assert is_vendor_enabled('zapaska', injected) is False


@pytest.mark.parametrize(
    ('service_type', 'folder'),
    [(ZapaskaService, 'zapaska'), (FourTochkiService, 'four_tochki'), (MimService, 'mim')],
)
def test_upload_uses_injected_provider_instead_of_global(
    tmp_path: Path,
    service_type: type[ZapaskaService] | type[FourTochkiService] | type[MimService],
    folder: str,
) -> None:
    global_provider = FakeConfigProvider(tmp_path / 'global')
    injected = FakeConfigProvider(tmp_path / 'injected')
    set_config_provider(global_provider)

    def configs_for(provider: FakeConfigProvider) -> dict[str, VendorConfig]:
        assert provider is injected
        return _configs(folder, enabled=False)

    with patch('services.vendor_activity.load_vendor_configs', side_effect=configs_for):
        assert service_type(injected).upload_data() is False


def test_upload_without_injected_provider_uses_current_global(
    fake_config_provider: FakeConfigProvider,
) -> None:
    with (
        patch('services.vendor_activity.load_vendor_configs', return_value={}) as load_configs,
        patch('services.zapaska_service.get_zapaska_api_config'),
        patch('services.zapaska_service.load_remote_vendor_data'),
    ):
        assert ZapaskaService().upload_data() is True

    load_configs.assert_called_once_with(fake_config_provider)
