"""tests for vendor registry"""

from unittest.mock import patch

from parsers.all_vendors import load_remote_vendor_data


def test_load_remote_vendor_data_uses_zapaska() -> None:
    """реестр вызывает загрузку API Запаски, а не run."""
    with patch("parsers.all_vendors.load_remote_data") as mock_load:
        load_remote_vendor_data()
        mock_load.assert_called_once_with()
