"""Протоколы стратегий для композиции BaseParser."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from parsers.row_item.row_item import RowItem

if TYPE_CHECKING:
    from parsers.xls_reader import IXlsReader


class ReaderFactory(Protocol):
    """Класс-ридер с фабричным get_instance (XlsReader / JsonPriceReader / Fake*)."""

    @classmethod
    def get_instance(cls, file_path: str, *args: Any, **kwargs: Any) -> IXlsReader: ...


class FileReaderProtocol(Protocol):
    """Чтение файлов прайсов и маппинг строк."""

    def raw_parse(self, path: str, parser_params: Any) -> list[dict[str, Any]]: ...

    def get_data_reader(self, path: str, parser_params: Any) -> IXlsReader: ...

    def price_files(self, parser_params: Any) -> list[str]: ...


class RowProcessorProtocol(Protocol):
    """Пошаговая обработка строк: наценка.

    Чистые утилиты (apply_min_rest, is_category_row, round_price и т.д.)
    вынесены в модульные функции row_processor.py — не часть протокола.
    """

    def _require_markup_policy(self) -> Any: ...

    def get_markup_percent(self, price_value: float) -> float: ...

    def add_price_markup(self, row_item: RowItem) -> None: ...


class TitleFilterProtocol(Protocol):  # noqa: WPS214
    """Подготовка title и фильтрация по стоп-словам / чёрному списку."""

    def get_prepared_title(self, row_item: RowItem) -> str: ...

    def set_prepared_title(self, row_item: RowItem) -> bool: ...

    def is_valid_title(self, title: str) -> bool: ...

    def has_stop_word(self, title: str) -> bool: ...

    def check_title_in_black_list(self, title: str) -> bool: ...

    def get_black_list(self) -> list[str]: ...

    def prepare_black_list(self, black_list: list[str]) -> list[str]: ...

    def get_stop_words(self) -> list[str]: ...

    def reset_caches(self) -> None: ...
