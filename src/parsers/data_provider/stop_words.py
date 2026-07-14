"""
stop words provider
"""

from cfg.main import MainConfig
from core.file_reader import read_file

from .black_list import BlackListProviderFromUserConfig


class StopWordsProviderBase:  # pylint: disable=too-few-public-methods
    """Base stop words data provider"""

    def get_stop_words_data(self):
        """Abstract method. Get stop words data."""
        raise NotImplementedError


class StopWordsProviderFromUserConfig(StopWordsProviderBase):  # pylint: disable=too-few-public-methods
    """Stop words data provider from user config file."""

    def get_stop_words_data(self):
        """Get stop words"""
        return BlackListProviderFromUserConfig.split_and_filtration(read_file(MainConfig().stop_words_file_path))
