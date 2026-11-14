"""Контекст общих настроек и читаемая запись пользовательского файла активации."""

from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.activation import activation_file, load_activation, set_vendor_enabled
from parsers.vendor_config.common import CommonVendorSettings
from parsers.vendor_config.slot_configs import BehaviorConfig, CategoryConfig, TitleConfig

_COMMON_PATH = 'custom/common-vendors.json'


@pytest.mark.parametrize('raw', [[], {'title_reference_order': 42}])
def test_common_settings_error_preserves_source(raw: object) -> None:
    """Неправильная структура указывает заданный источник общего конфига."""
    with pytest.raises(ConfigValidationError) as caught:
        CommonVendorSettings.from_dict(raw, _COMMON_PATH)

    assert str(caught.value).startswith(_COMMON_PATH)


def test_common_settings_keep_custom_source() -> None:
    """Адрес сохраняется и для последующей диагностики при наследовании."""
    settings = CommonVendorSettings.from_dict({}, _COMMON_PATH)

    assert settings.where == _COMMON_PATH


@pytest.mark.parametrize('field, invalid', [('rest', 42), ('pipeline', 'x')])
def test_direct_behavior_slot_error_preserves_source(field: str, invalid: object) -> None:
    """Прямой разбор behavior сохраняет источник без предварительной проверки имён стратегий."""
    with pytest.raises(ConfigValidationError) as caught:
        BehaviorConfig.from_dict({field: invalid}, _COMMON_PATH)

    assert str(caught.value).startswith(_COMMON_PATH)


def test_direct_strategy_slot_errors_preserve_source() -> None:
    """Оба публичных слота указывают источник ошибки типа strategy."""
    with pytest.raises(ConfigValidationError) as category_error:
        CategoryConfig.from_dict({'strategy': 42}, _COMMON_PATH)
    with pytest.raises(ConfigValidationError) as title_error:
        TitleConfig.from_dict({'strategy': 42}, _COMMON_PATH)

    assert str(category_error.value).startswith(_COMMON_PATH)
    assert str(title_error.value).startswith(_COMMON_PATH)


def test_activation_root_error_names_file(fake_config_provider: FakeConfigProvider) -> None:
    """Ошибка формы JSON называет пользовательский файл активации."""
    path = Path(activation_file(fake_config_provider))
    path.write_text('[]', encoding='utf-8')

    with pytest.raises(ConfigValidationError) as caught:
        load_activation(fake_config_provider)

    assert str(caught.value).startswith('vendor_activation.json')


def test_activation_file_is_readable_sorted_unicode(fake_config_provider: FakeConfigProvider) -> None:
    """Пользовательский JSON сохраняет Unicode, двухпробельные отступы и порядок ключей."""
    set_vendor_enabled('Поставщик', False, fake_config_provider)
    set_vendor_enabled('another', True, fake_config_provider)

    path = Path(activation_file(fake_config_provider))

    assert path.read_text(encoding='utf-8') == '{\n  "another": true,\n  "Поставщик": false\n}\n'
    assert load_activation(fake_config_provider) == {'another': True, 'Поставщик': False}
