"""
black list provider
"""

from fnmatch import fnmatchcase

from core.file_reader import read_file
from core.parse_paths import get_parse_paths

_CONFIG_FILE = "black_list"
_MASK_WILDCARD = "*"
_MSG_SKIPPED_BLACK_LIST = "\nОтброшено {count} позиций по правилам black_list."


def split_exact_and_masks(lines: list[str]) -> tuple[list[str], list[str]]:
    """Lines with * are glob masks; the rest are exact titles."""
    titles = [line for line in lines if _MASK_WILDCARD not in line]
    masks = [line for line in lines if _MASK_WILDCARD in line]
    return titles, masks


def title_matches_mask(title: str, mask: str) -> bool:
    """Case-insensitive glob: * matches any sequence in the title."""
    return fnmatchcase(title.lower(), mask.lower())


def skipped_black_list_message(count: int) -> str | None:
    """Summary of rows dropped by black_list exact titles and glob masks."""
    if not count:
        return None
    return _MSG_SKIPPED_BLACK_LIST.format(count=count)


class BlackListProviderBase:
    """Base black list data provider"""

    def get_black_list_data(self) -> list[str]:
        """Abstract method. Get exact titles."""
        raise NotImplementedError

    def get_stop_words_data(self) -> list[str]:
        """Abstract method. Get glob masks."""
        raise NotImplementedError


class BlackListProviderFromUserConfig(BlackListProviderBase):
    """Black list data provider from user config file."""

    def get_black_list_data(self) -> list[str]:
        """Exact titles from black_list (no wildcard)."""
        return self._load_entries()[0]

    def get_stop_words_data(self) -> list[str]:
        """Glob masks from black_list (lines containing *)."""
        return self._load_entries()[1]

    def _load_entries(self) -> tuple[list[str], list[str]]:
        raw = read_file(get_parse_paths().config_file(_CONFIG_FILE))
        return split_exact_and_masks(self.split_and_filtration(raw))

    @classmethod
    def split_and_filtration(cls, black_list: str) -> list[str]:
        """Split data from file by new-line and drop empty lines."""
        return [line.strip() for line in black_list.splitlines() if line.strip()]
