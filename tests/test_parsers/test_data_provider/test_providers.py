"""tests for black list and vendor list providers"""

from unittest.mock import patch

import pytest

from core.exceptions import CoreExceptionError
from core.parse_paths import ParsePaths
from parsers.data_provider.black_list import BlackListProviderBase, BlackListProviderFromUserConfig
from parsers.data_provider.vendor_list import (
    VendorListConfigFileError,
    VendorListProviderBase,
    VendorListProviderFromUserConfig,
)

_TO_LOG = "to_log"
_PATHS = ParsePaths(file_prices_folder="/prices", user_config_folder="/cfg")
_GET_PATHS = "parsers.data_provider.black_list.get_parse_paths"


def test_black_list_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        BlackListProviderBase().get_black_list_data()


def test_black_list_from_config() -> None:
    with (
        patch("parsers.data_provider.black_list.read_file", return_value="a\nb\n"),
        patch(_GET_PATHS, return_value=_PATHS),
    ):
        assert BlackListProviderFromUserConfig().get_black_list_data() == ["a", "b"]


def test_vendor_list_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        VendorListProviderBase().get_config_vendor_list()


def test_vendor_list_file_missing() -> None:
    with (
        patch.object(CoreExceptionError, _TO_LOG),
        patch(
            "parsers.data_provider.vendor_list.read_file",
            side_effect=FileNotFoundError,
        ),
        pytest.raises(VendorListConfigFileError),
    ):
        VendorListProviderFromUserConfig().get_config_vendor_list()
