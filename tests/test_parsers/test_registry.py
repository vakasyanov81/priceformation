"""tests for the config-driven vendor registry

Tests use the duplicated configs from ``tests/parse_config_example/vendors/``
(``example_vendors_provider``) with ``clear_vendor_configs_cache()`` to
guarantee fresh reads and independence from the real ``parse_config/vendors/``.
"""

from dataclasses import replace
from unittest.mock import MagicMock

import pytest

from domain.config_context import get_config_provider
from domain.product_groups import ProductGroup
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
    make_parse_config,
)
from parsers.base_parser.routing import VendorRouting
from parsers.registry import (
    UnknownVendorError,
    all_vendors_from_registry,
    clear_registry,
    make_vendor_entry,
    vendor_entry_for,
    vendor_markup_policy_for,
)
from parsers.vendor_config.group_models import TireAndDiskConfig
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.section_models import VendorSection
from parsers.vendor_config.slot_configs import BehaviorConfig

pytestmark = pytest.mark.usefixtures('example_vendors_provider')


def test_all_vendors_returns_entries() -> None:
    """all_vendors_from_registry возвращает только enabled вендоров."""
    clear_registry()
    provider = get_config_provider()
    entries = all_vendors_from_registry(provider)
    assert len(entries) > 0
    for parser_cls, config in entries:
        assert parser_cls is BaseParser
        assert config.config_provider is provider
        assert isinstance(config.routing, VendorRouting)
        assert isinstance(config, ParseConfiguration)
        assert config.vendor_section is not None
        assert config.vendor_config is not None
        assert config.is_enabled


def test_vendor_entry_for_finds_by_id() -> None:
    """vendor_entry_for находит секцию по id."""
    clear_registry()
    provider = get_config_provider()
    _, config = vendor_entry_for('2', provider)
    assert config.vendor_section.id == '2'
    assert config.vendor_section.name == 'Запаска (диски)'
    assert config.config_provider is provider
    assert isinstance(config.routing, VendorRouting)


def test_vendor_entry_for_finds_tire_section() -> None:
    """Запаска (шины) с id=22."""
    clear_registry()
    _, config = vendor_entry_for('22', get_config_provider())
    assert config.vendor_section.name == 'Запаска (шины)'


def test_vendor_entry_for_mim_returns_first_section() -> None:
    """Мим с id=4; первая секция = Легковая шина."""
    clear_registry()
    _, config = vendor_entry_for('4', get_config_provider())
    section = config.vendor_section
    assert section.id == '4'
    assert section.category.strategy == 'fixed'
    assert section.category.fixed_value == 'Легковая шина'


def test_vendor_entry_for_unknown_code_raises() -> None:
    """неизвестный код — UnknownVendorError с переданным кодом."""
    clear_registry()
    with pytest.raises(UnknownVendorError, match='nonexistent'):
        vendor_entry_for('nonexistent', get_config_provider())


def test_entries_carry_folder_and_vendor_config() -> None:
    """Записи несут папку поставщика и сам VendorConfig (не None)."""
    clear_registry()
    for _, config in all_vendors_from_registry(get_config_provider()):
        assert isinstance(config.vendor_config, VendorConfig)
        assert config.parser_params.supplier.folder_name == config.vendor_config.folder


def test_make_vendor_entry_attaches_section_and_config() -> None:
    """make_vendor_entry привязывает секцию и конфиг и берёт папку из folder."""
    vendor_cfg = VendorConfig(
        folder='my_folder',
        enabled=True,
        code='c',
        name='n',
    )
    section = VendorSection(
        id='c',
        name='n',
        start_row=1,
        file_templates=('p.xls',),
        columns={0: 'title'},
    )
    vendor_cfg = VendorConfig(
        folder=vendor_cfg.folder,
        code=vendor_cfg.code,
        name=vendor_cfg.name,
        product_groups=(TireAndDiskConfig((section,), BehaviorConfig()),),
    )

    provider = get_config_provider()
    _, config = make_vendor_entry(section, vendor_cfg, provider)

    assert config.config_provider is provider
    assert isinstance(config.routing, VendorRouting)
    assert config.vendor_section is section
    assert config.vendor_config is vendor_cfg
    assert config.product_group is ProductGroup.TIRE_AND_DISK
    assert config.parser_params.supplier.folder_name == 'my_folder'


def test_legacy_config_without_vendor_is_enabled_and_has_no_markup_policy() -> None:
    """Без привязанного VendorConfig поставщик считается включённым."""
    parser_params = ParserParams(
        supplier=ParseParamsSupplier(folder_name='f', name='n', code='c'),
        start_row=1,
        sheet_info='',
        columns={},
        stop_words=(),
        file_templates=(),
        sheet_indexes=(),
    )

    config = make_parse_config(parser_params, config_provider=MagicMock())

    assert config.is_enabled
    assert vendor_markup_policy_for(MagicMock(), config) is None


def test_standalone_section_has_no_routing() -> None:
    """Отдельная секция без групп поставщика использует прямое чтение прайса."""
    provider = get_config_provider()
    _, registered = vendor_entry_for('22', provider)
    assert registered.vendor_section is not None
    assert registered.vendor_config is not None
    standalone = replace(registered.vendor_config, product_groups=())

    parser_cls, config = make_vendor_entry(registered.vendor_section, standalone, provider)

    assert parser_cls is BaseParser
    assert config.routing is None
    assert config.vendor_section is registered.vendor_section
    assert config.vendor_config is standalone
    assert config.config_provider is provider


def test_is_enabled_for_disabled() -> None:
    """Выключенный поставщик (stk) — enabled=False."""
    clear_registry()
    _, config = vendor_entry_for('7', get_config_provider())
    assert not config.is_enabled


def test_is_enabled_for_enabled() -> None:
    """Включённый поставщик (mim) — enabled=True."""
    clear_registry()
    _, config = vendor_entry_for('4', get_config_provider())
    assert config.is_enabled


def test_vendor_markup_policy_from_config() -> None:
    """vendor_markup_policy_for строит политику из конфига секции."""
    clear_registry()
    _, config = vendor_entry_for('4', get_config_provider())
    policy = vendor_markup_policy_for(BaseParser, config)
    assert policy is not None


def test_stk_markup_is_six_percent_on_opt() -> None:
    """STK: карта % из `pricing.rules` конфига — 6% на закуп, РРЦ не учитывается."""
    clear_registry()
    _, config = vendor_entry_for('7', get_config_provider())
    policy = vendor_markup_policy_for(BaseParser, config)
    assert policy is not None
    assert policy.markup_percent_for_opt(1000) == pytest.approx(0.06)
    assert policy.apply(1000, 1500) == pytest.approx(1060)


def test_supplier_info_in_config() -> None:
    """ParseConfiguration несёт верные данные поставщика."""
    clear_registry()
    _, config = vendor_entry_for('22', get_config_provider())
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
    entries_before = all_vendors_from_registry(get_config_provider())
    clear_registry()
    entries_after = all_vendors_from_registry(get_config_provider())
    assert len(entries_before) == len(entries_after)


def test_all_vendors_returns_all_enabled() -> None:
    """all_vendors_from_registry возвращает только enabled вендоров."""
    clear_registry()
    entries = all_vendors_from_registry(get_config_provider())
    # autosnab (1 секция) + poshk (1) + four_tochki (2) + mim (3) + zapaska (2) = 9
    assert len(entries) == 9
    ids = {config.vendor_section.id for _, config in entries if config.vendor_section}
    assert ids == {'6', '1', '5', '55', '4', '42', '43', '2', '22'}
