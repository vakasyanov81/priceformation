"""Старую схему нельзя запустить через файловый источник, API или общие настройки."""

import json
from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.common import CommonVendorSettings
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.provider import load_vendor_configs


@pytest.mark.parametrize('source', ['xlsx', 'api'])
@pytest.mark.parametrize('enabled', [0, 1])
def test_legacy_source_requires_explicit_groups(
    fake_config_provider: FakeConfigProvider, source: str, enabled: int
) -> None:
    """Отключение поставщика и выбор API не включают временную совместимость."""
    folder = Path(fake_config_provider.config_file('vendors'))
    folder.mkdir(parents=True)
    legacy = {'file_templates': ['*.xlsx'], 'columns': {'0': 'title'}, 'sections': [{}]}
    payload = {'code': 'demo', 'name': 'Поставщик', 'source': source, 'api': legacy, **legacy}
    folder.joinpath('old.json').write_text(json.dumps(payload), encoding='utf-8')
    Path(fake_config_provider.config_file('vendor_activation.json')).write_text(
        json.dumps({'old': enabled}), encoding='utf-8'
    )
    with pytest.raises(ConfigValidationError) as caught:
        load_vendor_configs(fake_config_provider)
    assert 'old.json → product_groups' in str(caught.value)
    assert 'старый формат больше не поддерживается' in str(caught.value)
    assert 'tire_and_disk и явными id секций' in str(caught.value)


@pytest.mark.parametrize('key', ['columns', 'category', 'title', 'pricing', 'behavior'])
def test_legacy_common_defaults_require_groups(key: str) -> None:
    """Модельные общие настройки больше не принимаются без объявления групп."""
    with pytest.raises(ConfigValidationError) as caught:
        CommonVendorSettings.from_dict({'defaults': {key: {}}}, '_common.json')
    assert f'_common.json → defaults → {key}' in str(caught.value)
    assert 'product_groups[].defaults' in str(caught.value)


@pytest.mark.parametrize('group', ['tire_and_disk', 'batteries'])
def test_section_id_cannot_inherit_vendor_code(group: str) -> None:
    """Код поставщика не заменяет обязательный внешний ключ секции ни одной модели."""
    with pytest.raises(ConfigValidationError, match=r'demo\.json.*product_groups\[0\].*sections\[0\]\.id'):
        VendorConfig.from_dict(
            {
                'code': 'demo',
                'name': 'Поставщик',
                'product_groups': [{'id': group, 'file_templates': ['*.xlsx'], 'sections': [{}]}],
            },
            'demo',
            'demo.json',
        )
