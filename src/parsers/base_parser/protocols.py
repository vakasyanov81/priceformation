"""Протоколы стратегий для композиции BaseParser."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from domain.row_item.row_item import RowItem

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

    def require_markup_policy(self) -> Any: ...

    def get_markup_percent(self, price_value: float) -> float: ...

    def add_price_markup(self, row_item: RowItem) -> None: ...


class TitleFilterProtocol(Protocol):
    """Подготовка title и проверка его допустимости (граница, которую использует `TitleService`)."""

    def get_prepared_title(self, row_item: RowItem) -> str | None: ...

    def is_valid_title(self, title: str | None) -> bool: ...
