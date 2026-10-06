"""tests for the config-driven vendor registry

Tests use real configs from ``parse_config/vendors/`` with ``clear_vendor_configs_cache()``
to guarantee fresh reads.
"""

import pytest

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.registry import (
    UnknownVendorError,
    all_vendors_from_registry,
    clear_registry,
    register_vendor,
    vendor_config_is_enabled,
    vendor_entry_for,
    vendor_markup_policy_for,
)


def test_all_vendors_returns_entries() -> None:
    """all_vendors_from_registry возвращает только enabled вендоров."""
    clear_registry()
    entries = all_vendors_from_registry()
    assert len(entries) > 0
    for parser_cls, config in entries:
        assert parser_cls is BaseParser
        assert isinstance(config, ParseConfiguration)
        assert hasattr(config, '_vendor_section')
        assert hasattr(config, '_vendor_config')
        assert vendor_config_is_enabled(config)


def test_vendor_entry_for_finds_by_id() -> None:
    """vendor_entry_for находит секцию по id."""
    clear_registry()
    _, config = vendor_entry_for('2')
    assert config._vendor_section.id == '2'
    assert config._vendor_section.name == 'Запаска (диски)'


def test_vendor_entry_for_finds_tire_section() -> None:
    """Запаска (шины) с id=22."""
    clear_registry()
    _, config = vendor_entry_for('22')
    assert config._vendor_section.name == 'Запаска (шины)'


def test_vendor_entry_for_mim_returns_first_section() -> None:
    """Мим с id=4; первая секция = Легковая шина."""
    clear_registry()
    _, config = vendor_entry_for('4')
    section = config._vendor_section
    assert section.id == '4'
    assert section.category.strategy == 'fixed'
    assert section.category.fixed_value == 'Легковая шина'


def test_vendor_entry_for_unknown_code_raises() -> None:
    """неизвестный код — UnknownVendorError."""
    clear_registry()
    with pytest.raises(UnknownVendorError):
        vendor_entry_for('nonexistent')


def test_vendor_config_is_enabled_for_disabled() -> None:
    """Выключенный поставщик (poshk) — enabled=False."""
    clear_registry()
    _, config = vendor_entry_for('1')
    assert not vendor_config_is_enabled(config)


def test_vendor_config_is_enabled_for_enabled() -> None:
    """Включённый поставщик (mim) — enabled=True."""
    clear_registry()
    _, config = vendor_entry_for('4')
    assert vendor_config_is_enabled(config)


def test_vendor_markup_policy_from_config() -> None:
    """vendor_markup_policy_for строит политику из конфига секции."""
    clear_registry()
    _, config = vendor_entry_for('4')
    policy = vendor_markup_policy_for(BaseParser, config)
    assert policy is not None


def test_supplier_info_in_config() -> None:
    """ParseConfiguration несёт верные данные поставщика."""
    clear_registry()
    _, config = vendor_entry_for('22')
    assert config.supplier.code == '22'
    assert config.supplier.name == 'Запаска (шины)'
    assert config.supplier.folder_name == 'zapaska'


def test_register_vendor_is_noop() -> None:
    """register_vendor — no-op для обратной совместимости."""
    fake_vendor_type: object = type('FakeVendor', (), {})

    decorated = register_vendor('test_vendor', markup_policy='identity')(fake_vendor_type)
    assert decorated is fake_vendor_type
    assert decorated._markup_policy_type == 'identity'  # type: ignore[attr-defined]


def test_clear_registry_clears_cache() -> None:
    """clear_registry сбрасывает кэш конфигов."""
    clear_registry()
    entries_before = all_vendors_from_registry()
    clear_registry()
    entries_after = all_vendors_from_registry()
    assert len(entries_before) == len(entries_after)


def test_all_vendors_returns_all_enabled() -> None:
    """all_vendors_from_registry возвращает только enabled вендоров."""
    clear_registry()
    entries = all_vendors_from_registry()
    # autosnab (1 секция) + four_tochki (2) + mim (3) + zapaska (2) = 8
    assert len(entries) == 8
    ids = {config._vendor_section.id for _, config in entries}
    assert ids == {'6', '5', '4', '2', '22'}
