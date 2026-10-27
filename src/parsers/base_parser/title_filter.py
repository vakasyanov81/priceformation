"""Подготовка title и фильтрация по стоп-словам / чёрному списку."""

from functools import cached_property

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.data_provider.black_list import title_matches_mask


def strip_words_in_title(title: str) -> str:
    stripped_title = (title or '').strip()
    if not stripped_title:
        return title
    return ' '.join(_strip_chunks_title(title.split()))


def _strip_chunks_title(chunks: list[str]) -> list[str]:
    return [chunk.strip() for chunk in chunks if chunk.strip()]


class TitleBlockList:
    """Чёрный список и стоп-слова из конфига: читаются один раз при первом обращении."""

    def __init__(self, config: ParseConfiguration) -> None:
        self._config = config

    @cached_property
    def black_list(self) -> list[str]:
        return [strip_words_in_title(black_title) for black_title in self._config.black_list()]

    @cached_property
    def stop_words(self) -> list[str]:
        return self._config.stop_words()

    def blocks(self, title: str) -> bool:
        """Название попадает под стоп-слово (маску) или есть в чёрном списке."""
        if title in self.black_list:
            return True
        return any(title_matches_mask(title, mask) for mask in self.stop_words)


class TitleFilter:
    """Подготовка title и проверка его допустимости по конфигу."""

    def __init__(self, config: ParseConfiguration) -> None:
        self._block_list = TitleBlockList(config)

    def get_prepared_title(self, row_item: RowItem) -> str | None:
        return row_item.identity.title

    def is_valid_title(self, title: str | None) -> bool:
        return bool(title) and not self._block_list.blocks(title or '')
