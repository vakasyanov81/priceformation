"""tests for the active vendors collection (config-driven)"""

from parsers.all_vendors import all_vendor_supplier_catalog, all_vendor_supplier_info, split_vendor_supplier_info
from parsers.vendor_config.provider import clear_vendor_configs_cache


def test_supplier_info_maps_code_to_name() -> None:
    clear_vendor_configs_cache()
    supplier_info = all_vendor_supplier_info()
    assert supplier_info['2'] == 'Запаска (диски)'
    assert supplier_info['22'] == 'Запаска (шины)'


def test_catalog_maps_code_to_folder() -> None:
    """каталог: код → folder_name и название."""
    clear_vendor_configs_cache()
    catalog = all_vendor_supplier_catalog()
    assert catalog['1'] == {'sup_code': 'poshk', 'sup_title': 'Пошк'}
    assert catalog['4'] == {'sup_code': 'mim', 'sup_title': 'Мим'}
    assert catalog['2'] == {'sup_code': 'zapaska', 'sup_title': 'Запаска (диски)'}
    assert catalog['22'] == {'sup_code': 'zapaska', 'sup_title': 'Запаска (шины)'}


def test_split_separates_disabled() -> None:
    """enabled и disabled — разные словари код → имя."""
    clear_vendor_configs_cache()
    enabled, disabled = split_vendor_supplier_info()
    # enabled: те, у кого enabled: 1 (autosnab, mim, four_tochki, zapaska)
    assert '6' in enabled  # autosnab54_ru
    assert '5' in enabled  # four_tochki
    assert '4' in enabled  # mim
    assert '2' in enabled  # zapaska disk
    assert '22' in enabled  # zapaska tire
    # disabled: те, у кого enabled: 0 (poshk, stk, pioner)
    assert '1' in disabled  # poshk
    assert '7' in disabled  # stk
    assert '3' in disabled  # pioner
    # Убедимся, что нет пересечения
    for code in enabled:
        assert code not in disabled
