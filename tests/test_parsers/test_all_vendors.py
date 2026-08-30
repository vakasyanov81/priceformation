"""tests for the active vendors collection"""

from unittest.mock import MagicMock, patch

from parsers.all_vendors import all_vendor_supplier_info, split_vendor_supplier_info


def test_supplier_info_maps_code_to_name() -> None:
    supplier_info = all_vendor_supplier_info()
    assert supplier_info["2"] == "Запаска (диски)"
    assert supplier_info["22"] == "Запаска (шины)"


def test_split_separates_disabled() -> None:
    """enabled и disabled — разные словари код → имя."""
    pioner = MagicMock()
    pioner.supplier.code = "3"
    pioner.supplier.name = "Пионер"
    stk = MagicMock()
    stk.supplier.code = "7"
    stk.supplier.name = "STK"
    with (
        patch("parsers.all_vendors.all_vendors", return_value=[(None, pioner), (None, stk)]),
        patch("parsers.all_vendors.vendor_config_is_enabled", side_effect=[True, False]),
    ):
        enabled, disabled = split_vendor_supplier_info()
    assert enabled == {"3": "Пионер"}
    assert disabled == {"7": "STK"}
