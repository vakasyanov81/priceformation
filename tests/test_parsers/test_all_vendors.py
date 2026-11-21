"""tests for the active vendors collection (config-driven)"""

import pytest

from domain.config_context import get_config_provider
from parsers.all_vendors import all_vendor_supplier_catalog, all_vendor_supplier_info, split_vendor_supplier_info
from parsers.vendor_config.provider import clear_vendor_configs_cache

pytestmark = pytest.mark.usefixtures('example_vendors_provider')


def test_supplier_info_maps_code_to_name() -> None:
    clear_vendor_configs_cache()
    supplier_info = all_vendor_supplier_info(get_config_provider())
    assert supplier_info['2'] == 'Запаска (диски)'
    assert supplier_info['2-2'] == 'Запаска (шины)'


def test_catalog_maps_code_to_folder() -> None:
    """каталог: код → folder_name и название."""
    clear_vendor_configs_cache()
    catalog = all_vendor_supplier_catalog(get_config_provider())
    assert catalog['1'] == {'sup_code': 'poshk', 'sup_title': 'Пошк'}
    assert catalog['4'] == {'sup_code': 'mim', 'sup_title': 'Мим (шины)'}
    assert catalog['2'] == {'sup_code': 'zapaska', 'sup_title': 'Запаска (диски)'}
    assert catalog['2-2'] == {'sup_code': 'zapaska', 'sup_title': 'Запаска (шины)'}


def test_split_separates_disabled() -> None:
    """enabled и disabled — разные словари код → имя."""
    clear_vendor_configs_cache()
    enabled, disabled = split_vendor_supplier_info(get_config_provider())
    assert list(enabled) == ['1', '2', '4', '5', '6']
    assert list(disabled) == ['3', '7', '8']
    assert enabled['4'] == ['Мим (шины)', 'Мим (грузовые шины)', 'Мим (грузовые диски)']
    assert enabled['2'] == ['Запаска (диски)', 'Запаска (шины)']
    assert disabled['8'] == 'План-Т (Акб)'
