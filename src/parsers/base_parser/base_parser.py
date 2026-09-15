# flake8: noqa: WPS201
"""base parser logic — composition of FileReader, RowProcessor, TitleFilter."""

from re import sub as _re_sub
from typing import Any, Protocol

from core.exceptions import SupplierNotHavePricesError
from parsers import data_provider
from parsers.base_parser.base_parser_config import ParseConfigNotSetError, ParseConfiguration, ParserParams
from parsers.base_parser.base_parser_row import _keep_row_item, drop_empty_rest, enrich_items
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.base_parser.manufacturer_finder import ManufacturerFinder
from parsers.base_parser.markup_policy import MarkupPolicy, make_markup_policy
from parsers.base_parser.parse_statistic import ParseResultStatistic
from parsers.base_parser.price_markup import fill_percent_markup, get_markup as price_get_markup
from parsers.base_parser.protocols import FileReaderProtocol, RowProcessorProtocol, TitleFilterProtocol
from parsers.base_parser.row_processor import (
    RowProcessor,
    apply_min_rest,
    apply_manufacturer as apply_row_manufacturer,
    correction_category,
)
from parsers.base_parser.title_filter import TitleFilter
from parsers.row_item.row_item import RowItem
from parsers.xls_reader import IXlsReader, XlsReader

# Konstanta для get_spike_title (прототип была в base_parser_title).
_SPIKE_YES_VALUES = {'ш.', 'да'}

# Шаблон для замены запятой в числах.
_COMMA_RE = r'(\d),(\d)'
_COMMA_REPLACEMENT = r'\1.\2'
_CENTS = 10


class Parser(Protocol):
    """parser protocol"""

    @classmethod
    def supplier_folder_name(cls) -> str: ...

    def get_parsed_items(self) -> list[RowItem]: ...

    def parse(self) -> list[RowItem]: ...


class BaseParser:  # noqa: WPS214
    """Парсер — композиция FileReader, RowProcessor, TitleFilter."""

    find_manufacturer_on_enrich: bool = True

    def __init__(
        self,
        parse_config: ParseConfiguration | None = None,
        *,
        file_reader: FileReaderProtocol | None = None,
        data_reader: type[Any] | None = None,
        row_processor: RowProcessorProtocol | None = None,
        title_filter: TitleFilterProtocol | None = None,
    ) -> None:
        self.parsed_items: list[RowItem] = []
        self._parse_config = parse_config
        self.type_production: str | None = None
        self.data_reader = data_reader or XlsReader
        self.files: list[str] | None = None
        self.logger = LoggerParseProcess(repr(self))  # raises ParseConfigNotSetError if config is None
        self._category_finder: CategoryFinder | None = None
        self._manufacturer_finder: ManufacturerFinder | None = None
        self.unknown_category_skips: list[str] = []
        self.black_list_skips = 0

        self._file_reader_impl = file_reader or FileReader(data_reader=self.data_reader)
        self._row_processor = row_processor or RowProcessor()
        self._title_filter = title_filter or TitleFilter(self._parse_config)

    # ------------------------------------------------------------------
    # Config access
    # ------------------------------------------------------------------

    def parse_config(self) -> ParseConfiguration:
        if self._parse_config is None:
            raise ParseConfigNotSetError()
        return self._parse_config

    def set_parse_config(self, parse_config: ParseConfiguration) -> None:
        self._parse_config = parse_config
        self._manufacturer_finder = None
        self._title_filter.reset_caches()

    def parser_params(self) -> ParserParams:
        return self.parse_config().parser_params

    def manufacturer_finder(self) -> ManufacturerFinder:
        if self._manufacturer_finder is None:
            aliases = self.parse_config().manufacturer_aliases()
            self._manufacturer_finder = ManufacturerFinder(aliases)
        return self._manufacturer_finder

    def get_current_vendor_config(self) -> data_provider.VendorParams:
        folder_name = self.parser_params().supplier.folder_name
        vendor = self.parse_config().all_vendor_config().get(folder_name)
        return vendor or data_provider.VendorParams(enabled=0)

    @property
    def is_active(self) -> bool:
        return bool(self.get_current_vendor_config().enabled)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        supplier_name = self.parser_params().supplier.name
        sup_name = f'{class_name}: {supplier_name}'
        sheet_info = self.parser_params().sheet_info
        if sheet_info:
            sup_name = f'{sup_name} ({sheet_info})'
        return sup_name

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

    def parse(self) -> list[RowItem]:
        if not self.is_active:
            self.logger.log_disable_status()
            return []
        self._category_finder = CategoryFinder()
        self.files = self._price_files()
        self.logger.log_start()
        self.process()
        self.after_process()
        parsed = self.get_parsed_items()
        self.logger.log_finish(ParseResultStatistic(parsed))
        return parsed

    def process(self) -> int:
        """read → map → filter → enrich → vendor hook. Count before filters."""
        files = self.files or []
        self.logger.log_list_files(files)
        mapped = self.map_items(self.read_rows(files))
        raw_count = len(mapped)
        self.parsed_items += mapped
        self.parsed_items = self.filter_keep(self.parsed_items)
        self.parsed_items = self.enrich(self.parsed_items)
        self.apply_vendor_hooks(self.parsed_items)
        return raw_count

    def after_process(self) -> None:
        self.parsed_items = drop_empty_rest(self.parsed_items)
        fill_percent_markup(self.parsed_items)

    def enrich(self, row_items: list[RowItem]) -> list[RowItem]:
        return enrich_items(self, row_items)

    def filter_keep(self, row_items: list[RowItem]) -> list[RowItem]:
        return [row_item for row_item in row_items if _keep_row_item(self, row_item)]

    def apply_vendor_hooks(self, row_items: list[RowItem]) -> None:
        for row_item in row_items:
            self.process_parsed_row(row_item)

    # ------------------------------------------------------------------
    # File reading (delegates to FileReader)
    # ------------------------------------------------------------------

    def read_rows(self, paths: list[str]) -> list[dict[str, Any]]:
        raw_rows: list[dict[str, Any]] = []
        for price_file in paths:
            self.type_production = _type_production_from_filename(price_file)
            raw_rows.extend(self.raw_parse(price_file))
        return raw_rows

    def map_items(self, raw_rows: list[dict[str, Any]]) -> list[RowItem]:
        return [self.parser_params().row_item_adaptor(row_item) for row_item in raw_rows]

    def raw_parse(self, full_file_xls_path: str) -> list[dict[str, Any]]:
        return self._file_reader_impl.raw_parse(full_file_xls_path, self.parser_params())

    def get_data_reader(self, full_file_xls_path: str) -> IXlsReader:
        return self._file_reader_impl.get_data_reader(full_file_xls_path, self.parser_params())

    def get_parsed_items(self) -> list[RowItem]:
        return self.parsed_items

    def _price_files(self) -> list[str]:
        if self.files:
            return self.files
        files = self._file_reader_impl.price_files(self.parser_params())
        if not files:
            supplier_name = self.parser_params().supplier.name
            raise SupplierNotHavePricesError(f'Прайсов у поставщика ({supplier_name}) не обнаружено!')
        return files

    # ------------------------------------------------------------------
    # Row processing hooks (venders may override individual methods)
    # ------------------------------------------------------------------

    def process_parsed_row(self, row_item: RowItem) -> None:
        """После enrich: уникальное, min rest, категория, наценка."""
        self.after_row_mapped(row_item)
        self.skip_by_min_rest(row_item)
        self.apply_category(row_item)
        self.add_price_markup(row_item)

    def after_row_mapped(self, row_item: RowItem) -> None:
        """Редкое уникальное после enrich (title, fill_from_title). По умолчанию ничего."""

    def category_for(self, row_item: RowItem) -> str | None:
        """Категория строки. None — не менять type_production."""

    def apply_category(self, row_item: RowItem) -> None:
        category = self.category_for(row_item)
        if category is not None:
            row_item.type_production = category

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        apply_min_rest(row_item, self.get_item_rest(row_item), self.get_min_rest_count())

    @classmethod
    def get_item_rest(cls, row_item: RowItem) -> int:
        return row_item.rest_count

    @classmethod
    def get_min_rest_count(cls) -> int:
        return 4

    @classmethod
    def is_category_row(cls, row_item: RowItem) -> bool:
        return bool(row_item.title and not row_item.price_opt)

    def apply_manufacturer(self, row_item: RowItem) -> None:
        apply_row_manufacturer(row_item, self.find_manufacturer_on_enrich, self.manufacturer_finder())

    def correction_category(self, row_item: RowItem) -> None:
        correction_category(row_item, self._category_finder)

    def add_price_markup(self, row_item: RowItem) -> None:
        self._row_processor.add_price_markup(row_item)

    def get_markup_percent(self, price_value: float) -> float:
        return self._row_processor.get_markup_percent(price_value)

    @classmethod
    def round_price(cls, price_value: float) -> float:
        return -(-price_value // _CENTS) * _CENTS

    @classmethod
    def get_markup(cls, price: float, percent: float) -> float:
        return price_get_markup(price, percent)

    def _require_markup_policy(self) -> MarkupPolicy:
        return self._row_processor._require_markup_policy()

    # ------------------------------------------------------------------
    # Title (delegates to TitleFilter)
    # ------------------------------------------------------------------

    def get_prepared_title(self, row_item: RowItem) -> str:
        return self._title_filter.get_prepared_title(row_item)

    def set_prepared_title(self, row_item: RowItem) -> bool:
        prepared_title = self.get_prepared_title(row_item)
        title_is_prepared = row_item.title == prepared_title
        row_item.title = prepared_title or row_item.title
        return title_is_prepared

    def is_valid_title(self, title: str) -> bool:
        return self._title_filter.is_valid_title(title)

    def has_stop_word(self, title: str) -> bool:
        return self._title_filter.has_stop_word(title)

    def check_title_in_black_list(self, title: str) -> bool:
        return self._title_filter.check_title_in_black_list(title)

    def get_black_list(self) -> list[str]:
        return self._title_filter.get_black_list()

    def prepare_black_list(self, black_list: list[str]) -> list[str]:
        return self._title_filter.prepare_black_list(black_list)

    def get_stop_words(self) -> list[str]:
        return self._title_filter.get_stop_words()

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
        if not row_item.spike:
            return ''
        if row_item.spike.strip().lower() in _SPIKE_YES_VALUES:
            return 'Да'
        return ''


def _type_production_from_filename(price_file: str) -> str:
    """Последний суффикс имени файла после `_` (например disks.xls)."""
    return price_file.rsplit('_', maxsplit=1)[-1]


def make_parser[TParser: BaseParser](
    parser_cls: type[TParser],
    parse_config: ParseConfiguration,
    *,
    markup_policy: MarkupPolicy | None = None,
    file_prices: list[str] | None = None,
    data_reader: type[Any] | None = None,
) -> TParser:
    """Собрать парсер с политикой наценки. Не метод BaseParser."""
    policy = make_markup_policy(parse_config) if markup_policy is None else markup_policy
    kwargs: dict[str, Any] = {
        'parse_config': parse_config,
        'row_processor': RowProcessor(markup_policy=policy),
    }
    if data_reader is not None:
        kwargs['data_reader'] = data_reader
    parser = parser_cls(**kwargs)
    parser.files = file_prices
    return parser
