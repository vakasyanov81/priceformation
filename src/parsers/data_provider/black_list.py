"""
black list provider
"""

from cfg.main import MainConfig
from core.file_reader import read_file


class BlackListProviderBase:
    """Base black list data provider"""

    def get_black_list_data(self) -> list[str]:
        """Abstract method. Get black list data."""
        raise NotImplementedError


class BlackListProviderFromUserConfig(BlackListProviderBase):
    """Black list data provider from user config file."""

    def get_black_list_data(self) -> list[str]:
        """Get black list data"""
        black_list: str = read_file(MainConfig().black_list_file_path)
        return self.split_and_filtration(black_list)

    @classmethod
    def split_and_filtration(cls, black_list: str) -> list[str]:
        """Split data from file by `new-line` sign and filtration"""
        newline = "\n"
        split_lines = black_list.split(newline)
        split_lines = [black_title.strip(f" {newline}") for black_title in split_lines if black_title]
        split_lines = [black_title for black_title in split_lines if black_title]
        return split_lines
