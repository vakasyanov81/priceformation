"""tests for black list split helper"""

from parsers.data_provider.black_list import BlackListProviderFromUserConfig


def test_split_black_list():
    """split and strip lines from raw text"""
    assert ["test1", "test2"] == BlackListProviderFromUserConfig().split_and_filtration("test1\n test2")
