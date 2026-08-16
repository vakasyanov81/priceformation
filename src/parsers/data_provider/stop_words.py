"""
stop words provider
"""

from core.file_reader import read_file
from core.parse_paths import get_parse_paths

from .black_list import BlackListProviderFromUserConfig

_CONFIG_FILE = "stop_words"


class StopWordsProviderBase:
    """Base stop words data provider"""

    def get_stop_words_data(self) -> list[str]:
        """Abstract method. Get stop words data."""
        raise NotImplementedError


class StopWordsProviderFromUserConfig(StopWordsProviderBase):
    """Stop words data provider from user config file."""

    def get_stop_words_data(self) -> list[str]:
        """Get stop words"""
        return BlackListProviderFromUserConfig.split_and_filtration(
            read_file(get_parse_paths().config_file(_CONFIG_FILE)),
        )
