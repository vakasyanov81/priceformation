"""
black list provider
"""

from core.file_reader import read_file
from core.parse_paths import get_parse_paths

_CONFIG_FILE = "black_list"


class BlackListProviderBase:
    """Base black list data provider"""

    def get_black_list_data(self) -> list[str]:
        """Abstract method. Get black list data."""
        raise NotImplementedError


class BlackListProviderFromUserConfig(BlackListProviderBase):
    """Black list data provider from user config file."""

    def get_black_list_data(self) -> list[str]:
        """Get black list data"""
        black_list: str = read_file(get_parse_paths().config_file(_CONFIG_FILE))
        return self.split_and_filtration(black_list)

    @classmethod
    def split_and_filtration(cls, black_list: str) -> list[str]:
        """Split data from file by new-line and drop empty lines."""
        return [line.strip() for line in black_list.splitlines() if line.strip()]
