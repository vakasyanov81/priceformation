"""tests for black list provider"""

from unittest.mock import MagicMock, patch

import pytest

from parsers.data_provider.black_list import BlackListProviderBase, BlackListProviderFromUserConfig


def test_black_list_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        BlackListProviderBase().get_black_list_data()


def test_black_list_masks_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        BlackListProviderBase().get_stop_words_data()


def test_black_list_from_config() -> None:
    config_provider = MagicMock()
    with patch('parsers.data_provider.black_list.read_file', return_value='a\nb\n') as read:
        provider = BlackListProviderFromUserConfig(config_provider)
        assert provider.get_black_list_data() == ['a', 'b']
        assert provider.get_stop_words_data() == []
    read.assert_called_with(config_provider.config_file.return_value)
    config_provider.config_file.assert_called_with('black_list')


def test_black_list_from_config_splits_masks() -> None:
    raw = 'exact title\n*некондиция*\n*2 сорт*\n'
    with patch('parsers.data_provider.black_list.read_file', return_value=raw):
        provider = BlackListProviderFromUserConfig(MagicMock())
        assert provider.get_black_list_data() == ['exact title']
        assert provider.get_stop_words_data() == ['*некондиция*', '*2 сорт*']
