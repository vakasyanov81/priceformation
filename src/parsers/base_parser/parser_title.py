"""Название позиции в BaseParser: текстовые хелперы и подготовка title (делегирует TitleFilter и стратегии)."""

from re import sub as _re_sub

from domain.row_item.markdown_title import is_markdown_title
from domain.row_item.production_plant import production_plant
from domain.row_item.production_year import production_year
from domain.row_item.row_item import RowItem
from parsers.base_parser.parser_files import ParserFiles

# Значения признака шипов, считающиеся «Да».
_SPIKE_YES_VALUES = {'ш.', 'да'}

# Шаблон для замены запятой в числах.
_COMMA_RE = r'(\d),(\d)'
_COMMA_REPLACEMENT = r'\1.\2'


class ParserTitleText(ParserFiles):
    """Текстовые хелперы названия, переопределяемые поставщиками."""

    @classmethod
    def prepare_title(cls, title: str) -> str:
        chunks = cls.strip_chunks_title(title.split())
        chunks = cls._prepare_title_chunks(chunks)
        return _re_sub(_COMMA_RE, _COMMA_REPLACEMENT, ' '.join(chunks))

    @classmethod
    def _prepare_title_chunks(cls, chunks: list[str]) -> list[str]:
        return chunks

    @classmethod
    def strip_chunks_title(cls, chunks: list[str]) -> list[str]:
        return [chunk.strip() for chunk in chunks if chunk.strip()]

    @classmethod
    def strip_words_in_title(cls, title: str) -> str:
        stripped_title = (title or '').strip()
        if not stripped_title:
            return title
        return ' '.join(cls.strip_chunks_title(title.split()))

    @classmethod
    def get_spike_title(cls, row_item: RowItem) -> str:
        if not row_item.tire.spike:
            return ''
        if row_item.tire.spike.strip().lower() in _SPIKE_YES_VALUES:
            return 'Да'
        return ''


class ParserTitle(ParserTitleText):
    """Подготовка title позиции: стратегия или дефолтный фильтр."""

    def get_prepared_title(self, row_item: RowItem) -> str | None:
        """Подготовить title: стратегия или дефолт."""
        if self._strategy_hooks and self._strategy_hooks.title is not None:
            return self._strategy_hooks.title.prepare(row_item)
        return self._title_filter.get_prepared_title(row_item)

    def set_prepared_title(self, row_item: RowItem) -> bool:
        """Подготовить title; уценка, год и завод читаются и из текста поставщика: собранное название их не несёт."""
        source_title = row_item.identity.title
        prepared_title = self.get_prepared_title(row_item)
        title_is_prepared = source_title == prepared_title
        row_item.set_field('title', prepared_title or source_title)
        if is_markdown_title(source_title) or is_markdown_title(row_item.identity.title):
            row_item.set_field('marked_down', True)
        year = production_year(source_title) or production_year(row_item.identity.title)
        if year:
            row_item.set_field('production_year', year)
        plant = production_plant(source_title) or production_plant(row_item.identity.title)
        if plant:
            row_item.set_field('production_plant', plant)
        return title_is_prepared

    def is_valid_title(self, title: str | None) -> bool:
        return self._title_filter.is_valid_title(title)
