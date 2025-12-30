from parsers.data_provider.black_list import BlackListProviderFromUserConfig


def test_split_black_list() -> None:
    assert ["test1", "test2"] == BlackListProviderFromUserConfig().split_and_filtration("test1\n test2")
