"""Очередь поставщиков-эталонов названия из `title_reference_order` общих настроек."""

from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.provider import clear_vendor_configs_cache
from parsers.vendor_config.reference_priority import load_reference_priority

_VENDOR = (
    '{{"code": "{code}", "name": "{name}", "file_templates": ["*.xls"], '
    '"sections": [{{"name": "{name} (шины)", "columns": {{"1": "title"}}}}]}}'
)


def _folder(provider: FakeConfigProvider) -> Path:
    folder = Path(provider.config_file('vendors'))
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _write(provider: FakeConfigProvider, stem: str, name: str) -> None:
    config = _VENDOR.format(code=stem, name=name)
    _folder(provider).joinpath(f'{stem}.json').write_text(config, encoding='utf-8')


def _write_order(provider: FakeConfigProvider, order: str) -> None:
    _folder(provider).joinpath('_common.json').write_text(f'{{"title_reference_order": {order}}}', encoding='utf-8')
    clear_vendor_configs_cache()


def test_priority_is_set_for_vendor_and_its_sections(fake_config_provider: FakeConfigProvider) -> None:
    """Место по порядку в списке действует на имя поставщика и имена его секций; вне списка — нет в карте."""
    _write(fake_config_provider, 'a', 'Первый')
    _write(fake_config_provider, 'b', 'Второй')
    _write(fake_config_provider, 'c', 'Безымянный')
    _write_order(fake_config_provider, '["b", "a"]')

    assert load_reference_priority() == {'Второй': 1, 'Второй (шины)': 1, 'Первый': 2, 'Первый (шины)': 2}


def test_without_common_file_priority_is_empty(fake_config_provider: FakeConfigProvider) -> None:
    _write(fake_config_provider, 'a', 'Первый')
    clear_vendor_configs_cache()

    assert not load_reference_priority()


def test_unknown_vendor_in_order_rejected(fake_config_provider: FakeConfigProvider) -> None:
    """Опечатка в имени поставщика — ошибка с путём до ключа, а не молча пропущенный эталон."""
    _write(fake_config_provider, 'a', 'Первый')
    _write_order(fake_config_provider, '["a", "zz"]')

    with pytest.raises(ConfigValidationError, match='title_reference_order: нет поставщика «zz»'):
        load_reference_priority()
