"""Тесты сервиса активации поставщиков: список и переключение флага."""

from pathlib import Path

from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.provider import clear_vendor_configs_cache
from services.vendor_activation import VendorActivationService, VendorState

_FOLDER = 'vendors'


def _config(code: str, name: str, *, enabled: int) -> str:
    return (
        f'{{"enabled": {enabled}, "code": "{code}", "name": "{name}", '
        '"start_row": 1, "file_templates": ["*.xls"], "sections": [{"columns": {"1": "title"}}]}'
    )


def _write_vendors(provider: FakeConfigProvider, files: dict[str, str]) -> None:
    folder = Path(provider.config_file(_FOLDER))
    folder.mkdir(parents=True, exist_ok=True)
    for file_name, text in files.items():
        folder.joinpath(file_name).write_text(text, encoding='utf-8')
    clear_vendor_configs_cache()


def test_list_vendors_sorted_by_name(fake_config_provider: FakeConfigProvider) -> None:
    """Список идёт по названию и несёт текущий флаг активности."""
    _write_vendors(
        fake_config_provider,
        {
            'bbb.json': _config('1', 'Omega', enabled=0),
            'aaa.json': _config('2', 'Alpha', enabled=1),
        },
    )

    states = VendorActivationService().list_vendors()

    assert states == [VendorState('aaa', 'Alpha', True), VendorState('bbb', 'Omega', False)]


def test_toggle_flips_flag_and_persists(fake_config_provider: FakeConfigProvider) -> None:
    """toggle меняет флаг в памяти и в файле конфига."""
    _write_vendors(fake_config_provider, {'stk.json': _config('7', 'STK', enabled=0)})
    service = VendorActivationService()

    assert service.toggle('stk') == VendorState('stk', 'STK', True)
    assert service.list_vendors()[0].enabled is True
    path = Path(fake_config_provider.config_file(f'{_FOLDER}/stk.json'))
    assert '"enabled": 1' in path.read_text(encoding='utf-8')

    assert service.toggle('stk') == VendorState('stk', 'STK', False)
    assert '"enabled": 0' in path.read_text(encoding='utf-8')
