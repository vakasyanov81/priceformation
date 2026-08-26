"""Title preparation and stop/black-list checks."""

from parsers.base_parser.base_parser_access import ParserConfigAccess
from parsers.row_item.row_item import RowItem

_SPIKE_YES = {"ш.", "да"}
_SEASON_TITLES = {"зима": "Зимняя", "лето": "Летняя"}


def replace_season(row_item: RowItem) -> str | None:
    """Каноническое имя сезона или исходная строка."""
    if not row_item.season:
        return None
    return _SEASON_TITLES.get(row_item.season.lower()) or row_item.season


class ParserTitleOps:
    def get_prepared_title(self, row_item: RowItem) -> str:
        return row_item.title

    def set_prepared_title(self, row_item: RowItem) -> bool:
        prepared_title = self.get_prepared_title(row_item)
        title_is_prepared = row_item.title == prepared_title
        row_item.title = prepared_title or row_item.title
        return title_is_prepared

    @classmethod
    def prepare_title(cls, title: str) -> str:
        """prepare title"""
        chunks = cls.strip_chunks_title(title.split())
        chunks = cls._prepare_title_chunks(chunks)
        return " ".join(chunks)

    @classmethod
    def _prepare_title_chunks(cls, chunks: list[str]) -> list[str]:
        return chunks

    @classmethod
    def strip_chunks_title(cls, chunks: list[str]) -> list[str]:
        """# [" 385/65  ", " R22.5", ...] -> ["385/65", "R22.5", ...]"""
        return [chunk.strip() for chunk in chunks if chunk.strip()]

    @classmethod
    def strip_words_in_title(cls, title: str) -> str:
        """ " 385/65   R22.5..." -> "385/65 R22.5..." """
        stripped_title = (title or "").strip()
        if not stripped_title:
            return title
        return " ".join(cls.strip_chunks_title(title.split()))

    @classmethod
    def get_spike_title(cls, row_item: RowItem) -> str:
        """Наличие шипа"""
        if not row_item.spike:
            return ""
        if row_item.spike.strip().lower() in _SPIKE_YES:
            return "Да"
        return ""


class ParserTitleFilters(ParserTitleOps, ParserConfigAccess):
    def get_black_list(self) -> list[str]:
        if self._black_list is None:
            self._black_list = self.prepare_black_list(self.parse_config().black_list())
        return self._black_list

    def prepare_black_list(self, black_list: list[str]) -> list[str]:
        return [self.strip_words_in_title(black_title) for black_title in black_list]

    def get_stop_words(self) -> list[str]:
        if self._stop_words is None:
            self._stop_words = self.parse_config().stop_words()
        return self._stop_words

    def is_valid_title(self, title: str) -> bool:
        has_content = bool(title)
        no_stop = not self.has_stop_word(title)
        not_blacklisted = not self.check_title_in_black_list(title)
        return has_content and no_stop and not_blacklisted

    def has_stop_word(self, title: str) -> bool:
        title_lower = title.lower()
        return any(s_word.lower() in title_lower for s_word in self.get_stop_words())

    def check_title_in_black_list(self, title: str) -> bool:
        return title in self.get_black_list()
