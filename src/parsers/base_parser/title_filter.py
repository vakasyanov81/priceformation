"""Подготовка title и фильтрация по стоп-словам / чёрному списку."""

from typing import Any

from parsers.base_parser.base_parser_config import ParseConfigNotSetError
from parsers.data_provider.black_list import title_matches_mask
from parsers.row_item.row_item import RowItem

# --- Модульные функции (бывшие @staticmethod) ---


def strip_words_in_title(title: str) -> str:
    stripped_title = (title or '').strip()
    if not stripped_title:
        return title
    return ' '.join(_strip_chunks_title(title.split()))


def _strip_chunks_title(chunks: list[str]) -> list[str]:
    return [chunk.strip() for chunk in chunks if chunk.strip()]


class TitleFilter:  # noqa: WPS214
    """Title preparation and stop/black-list checks by config."""

    def __init__(self, config: Any) -> None:
        self._config = config
        self._black_list: list[str] | None = None
        self._stop_words: list[str] | None = None

    def reset_caches(self) -> None:
        self._black_list = None
        self._stop_words = None

    def _parse_config(self) -> Any:
        if self._config is None:
            raise ParseConfigNotSetError()
        return self._config

    def get_black_list(self) -> list[str]:
        if self._black_list is None:
            self._black_list = self.prepare_black_list(self._parse_config().black_list())
        return self._black_list

    def prepare_black_list(self, black_list: list[str]) -> list[str]:
        return [strip_words_in_title(black_title) for black_title in black_list]

    def get_stop_words(self) -> list[str]:
        if self._stop_words is None:
            self._stop_words = self._parse_config().stop_words()
        return self._stop_words

    def get_prepared_title(self, row_item: RowItem) -> str:
        return row_item.title

    def set_prepared_title(self, row_item: RowItem) -> bool:
        prepared_title = self.get_prepared_title(row_item)
        title_is_prepared = row_item.title == prepared_title
        row_item.title = prepared_title or row_item.title
        return title_is_prepared

    def is_valid_title(self, title: str) -> bool:
        has_content = bool(title)
        no_stop = not self.has_stop_word(title)
        not_blacklisted = not self.check_title_in_black_list(title)
        return has_content and no_stop and not_blacklisted

    def has_stop_word(self, title: str) -> bool:
        return any(title_matches_mask(title, mask) for mask in self.get_stop_words())

    def check_title_in_black_list(self, title: str) -> bool:
        return title in self.get_black_list()
