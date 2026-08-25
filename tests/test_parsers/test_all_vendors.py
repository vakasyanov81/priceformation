"""tests for the active vendors collection"""

from parsers.all_vendors import all_vendor_supplier_info


def test_supplier_info_maps_code_to_name() -> None:
    supplier_info = all_vendor_supplier_info()
    assert supplier_info["2"] == "Запаска (диски)"
    assert supplier_info["22"] == "Запаска (шины)"
