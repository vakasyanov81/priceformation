"""tests for black list and vendor list providers"""

from unittest.mock import patch

import pytest

from core.exceptions import CoreExceptionError
from parsers.data_provider.black_list import BlackListProviderBase, BlackListProviderFromUserConfig
from parsers.data_provider.vendor_list import (
    VendorListConfigFileError,
    VendorListProviderBase,
    VendorListProviderFromUserConfig,
)

_TO_LOG = "to_log"


def test_black_list_base_raises():
    with pytest.raises(NotImplementedError):
        BlackListProviderBase().get_black_list_data()


def test_black_list_from_config():
    with (
        patch("parsers.data_provider.black_list.read_file", return_value="a\nb\n"),
        patch("parsers.data_provider.black_list.MainConfig") as mock_cfg,
    ):
        mock_cfg.return_value.black_list_file_path = "/x"
        assert BlackListProviderFromUserConfig().get_black_list_data() == ["a", "b"]


def test_vendor_list_base_raises():
    with pytest.raises(NotImplementedError):
        VendorListProviderBase().get_config_vendor_list()


def test_vendor_list_file_missing():
    with (
        patch.object(CoreExceptionError, _TO_LOG),
        patch(
            "parsers.data_provider.vendor_list.read_file",
            side_effect=FileNotFoundError,
        ),
        patch("parsers.data_provider.vendor_list.MainConfig") as mock_cfg,
        pytest.raises(VendorListConfigFileError),
    ):
        mock_cfg.return_value.vendor_list_file_path = "/missing"
        mock_cfg.return_value.vendor_list_file_name = "v.json"
        VendorListProviderFromUserConfig().get_config_vendor_list()
