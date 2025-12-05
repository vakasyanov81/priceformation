"""
black list provider
"""

from cfg.main import MainConfig
from core.file_reader import read_file


class BlackListProviderBase:
    """Base black list data provider"""

    def get_black_list_data(self):
        """Abstract method. Get black list data."""
        raise NotImplementedError


class BlackListProviderFromUserConfig(BlackListProviderBase):
    """Black list data provider from user config file."""

    def get_black_list_data(self):
        """Get black list data"""
        black_list = read_file(MainConfig().black_list_file_path) or ""
        return self.split_and_filtration(black_list)

    @classmethod
    def split_and_filtration(cls, black_list: str):
        """Split data from file by `new-line` sign and filtration"""
        _newline = "\n"
        _black_list = black_list.split(_newline)
        _black_list = [black_title.strip(f" {_newline}") for black_title in _black_list if black_title]
        _black_list = [black_title for black_title in _black_list if black_title]
        return black_list
