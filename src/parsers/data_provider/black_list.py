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
        """Split data from file by new-line and drop empty lines."""
        return [line.strip() for line in black_list.splitlines() if line.strip()]
