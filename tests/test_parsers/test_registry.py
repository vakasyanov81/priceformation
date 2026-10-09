"""tests for the config-driven vendor registry

Tests use the duplicated configs from ``tests/parse_config_example/vendors/``
(``example_vendors_provider``) with ``clear_vendor_configs_cache()`` to
guarantee fresh reads and independence from the real ``parse_config/vendors/``.
"""

import pytest

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
    make_parse_config,
)
from parsers.registry import (
    UnknownVendorError,
    all_vendors_from_registry,
    clear_registry,
    make_vendor_entry,
    vendor_config_is_enabled,
    vendor_entry_for,
    vendor_markup_policy_for,
)
from parsers.vendor_config.models import VendorConfig, VendorSection

pytestmark = pytest.mark.usefixtures('example_vendors_provider')


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
    """неизвестный код — UnknownVendorError с переданным кодом."""
    clear_registry()
    with pytest.raises(UnknownVendorError, match='nonexistent'):
        vendor_entry_for('nonexistent')


def test_entries_carry_folder_and_vendor_config() -> None:
    """Записи несут папку поставщика и сам VendorConfig (не None)."""
    clear_registry()
    for _, config in all_vendors_from_registry():
        assert isinstance(config._vendor_config, VendorConfig)
        assert config.parser_params.supplier.folder_name == config._vendor_config.folder


def test_make_vendor_entry_attaches_section_and_config() -> None:
    """make_vendor_entry привязывает секцию и конфиг и берёт папку из folder."""
    vendor_cfg = VendorConfig(folder='my_folder', enabled=True, code='c', name='n', start_row=1)
    section = VendorSection(
        id='c',
        name='n',
        start_row=1,
        file_templates=('p.xls',),
        columns={0: 'title'},
    )

    _, config = make_vendor_entry(section, vendor_cfg)

    assert config._vendor_section is section
    assert config._vendor_config is vendor_cfg
    assert config.parser_params.supplier.folder_name == 'my_folder'


def test_vendor_config_is_enabled_without_vendor_config() -> None:
    """Без привязанного VendorConfig поставщик считается включённым."""
    parser_params = ParserParams(
        supplier=ParseParamsSupplier(folder_name='f', name='n', code='c'),
        start_row=1,
        sheet_info='',
        columns={},
        stop_words=(),
        file_templates=(),
        sheet_indexes=(),
        row_item_adaptor=RowItem,
    )

    assert vendor_config_is_enabled(make_parse_config(parser_params))


def test_vendor_config_is_enabled_for_disabled() -> None:
    """Выключенный поставщик (stk) — enabled=False."""
    clear_registry()
    _, config = vendor_entry_for('7')
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


def test_register_vendor_is_removed() -> None:
    """register_vendor больше не существует — легаси-вендоры удалены."""
    import parsers.registry as registry_mod

    assert not hasattr(registry_mod, 'register_vendor')


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
    # autosnab (1 секция) + poshk (1) + four_tochki (2) + mim (3) + zapaska (2) = 9
    assert len(entries) == 9
    ids = {config._vendor_section.id for _, config in entries}
    assert ids == {'6', '1', '5', '4', '2', '22'}
