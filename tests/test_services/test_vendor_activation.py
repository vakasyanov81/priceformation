"""Тесты сервиса активации поставщиков: список и переключение флага."""

import json
from pathlib import Path

from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.provider import clear_vendor_configs_cache
from services.vendor_activation import VendorActivationService, VendorState

_FOLDER = 'vendors'
_ACTIVATION_FILE = 'vendor_activation.json'


def _config(code: str, name: str) -> str:
    return (
        f'{{"code": "{code}", "name": "{name}", '
        '"start_row": 1, "file_templates": ["*.xls"], "sections": [{"columns": {"1": "title"}}]}'
    )


def _write_vendors(provider: FakeConfigProvider, files: dict[str, str]) -> None:
    folder = Path(provider.config_file(_FOLDER))
    folder.mkdir(parents=True, exist_ok=True)
    for file_name, text in files.items():
        folder.joinpath(file_name).write_text(text, encoding='utf-8')
    clear_vendor_configs_cache()


def test_list_vendors_sorted_by_name(fake_config_provider: FakeConfigProvider) -> None:
    """Список идёт по названию и несёт текущий флаг активности из vendor_activation.json."""
    _write_vendors(
        fake_config_provider,
        {
            'bbb.json': _config('1', 'Omega'),
            'aaa.json': _config('2', 'Alpha'),
        },
    )
    Path(fake_config_provider.config_file(_ACTIVATION_FILE)).write_text('{"bbb": 0}', encoding='utf-8')
    clear_vendor_configs_cache()

    states = VendorActivationService().list_vendors()

    assert states == [VendorState('aaa', 'Alpha', True), VendorState('bbb', 'Omega', False)]


def test_toggle_flips_flag_and_persists(fake_config_provider: FakeConfigProvider) -> None:
    """toggle меняет флаг в памяти и в vendor_activation.json; конфиг поставщика не меняется."""
    stk_source = _config('7', 'STK')
    _write_vendors(fake_config_provider, {'stk.json': stk_source})
    service = VendorActivationService()
    activation = Path(fake_config_provider.config_file(_ACTIVATION_FILE))

    assert service.toggle('stk') == VendorState('stk', 'STK', False)
    assert service.list_vendors()[0].enabled is False
    assert json.loads(activation.read_text(encoding='utf-8')) == {'stk': 0}

    assert service.toggle('stk') == VendorState('stk', 'STK', True)
    assert json.loads(activation.read_text(encoding='utf-8')) == {'stk': 1}
    assert Path(fake_config_provider.config_file(f'{_FOLDER}/stk.json')).read_text(encoding='utf-8') == stk_source


def test_service_uses_injected_provider(tmp_path: Path) -> None:
    """Список и переключение идут через переданный провайдер, а не глобальный."""
    provider = FakeConfigProvider(tmp_path, config_folder=tmp_path / 'parse_config')
    vendors = Path(provider.config_file('vendors'))
    vendors.mkdir(parents=True)
    vendors.joinpath('mim.json').write_text(
        '{"code": "mim", "name": "Мим", "start_row": 2, "file_templates": ["*.xls"],'
        ' "sections": [{"columns": {"1": "manufacturer_name"}}]}',
        encoding='utf-8',
    )
    service = VendorActivationService(config_provider=provider)

    assert [state.folder for state in service.list_vendors()] == ['mim']
    assert service.toggle('mim').enabled is False
    assert Path(provider.config_file('vendor_activation.json')).is_file()
