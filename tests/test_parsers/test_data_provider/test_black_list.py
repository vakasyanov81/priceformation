"""tests for black list split helper"""

from parsers.data_provider.black_list import BlackListProviderFromUserConfig


def test_split_black_list() -> None:
    """split and strip lines from raw text"""
    assert ["test1", "test2"] == BlackListProviderFromUserConfig().split_and_filtration("test1\n test2")


def test_split_keeps_spaces_inside_line() -> None:
    """пробел внутри строки не является разделителем"""
    assert BlackListProviderFromUserConfig.split_and_filtration("foo bar\nbaz") == ["foo bar", "baz"]
