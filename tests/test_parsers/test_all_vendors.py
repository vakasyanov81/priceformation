"""tests for the active vendors collection (config-driven)"""

from dataclasses import replace
from pathlib import Path
from shutil import copytree
from unittest.mock import patch

import pytest

from domain.config_context import get_config_provider
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.all_vendors import all_vendor_supplier_catalog, all_vendor_supplier_info, split_vendor_supplier_info
from parsers.vendor_config.provider import clear_vendor_configs_cache, load_vendor_configs

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


def test_split_separates_disabled_by_supplier_folder() -> None:
    """enabled и disabled — разные словари папка → названия секций."""
    clear_vendor_configs_cache()
    enabled, disabled = split_vendor_supplier_info(get_config_provider())
    assert list(enabled) == ['poshk', 'zapaska', 'mim', 'four_tochki', 'autosnab54_ru']
    assert list(disabled) == ['pioner', 'stk', 'plant']
    assert enabled['mim'] == ['Мим (шины)', 'Мим (грузовые шины)', 'Мим (грузовые диски)']
    assert enabled['zapaska'] == ['Запаска (диски)', 'Запаска (шины)']
    assert disabled['plant'] == 'План-Т (Акб)'


def test_split_covers_every_vendor_config_folder(tmp_path: Path) -> None:
    """Каждый файл поставщика представлен ровно одним ключом сводки."""
    provider = FakeConfigProvider(tmp_path)
    vendors_folder = Path(provider.config_file('vendors'))
    copytree(get_config_provider().config_file('vendors'), vendors_folder)
    vendors_folder.joinpath('_common.json').write_text('{}', encoding='utf-8')
    config_files = vendors_folder.glob('*.json')
    config_folders = {path.stem for path in config_files if not path.name.startswith('_')}

    enabled, disabled = split_vendor_supplier_info(provider)

    assert set(enabled) | set(disabled) == config_folders
    assert not set(enabled) & set(disabled)


def test_split_sorts_numeric_codes_before_text_codes() -> None:
    """Порядок сводки задаёт код поставщика, а не имя папки."""
    configs = load_vendor_configs(get_config_provider())
    reordered = {
        'mim': replace(configs['mim'], code='alpha'),
        'poshk': replace(configs['poshk'], code='20'),
        'zapaska': replace(configs['zapaska'], code='3'),
    }
    with patch('parsers.all_vendors.load_vendor_configs', return_value=reordered):
        enabled, _ = split_vendor_supplier_info(get_config_provider())

    assert list(enabled) == ['zapaska', 'poshk', 'mim']
