"""
base parser logic
"""

import math
from pathlib import Path
from typing import Any, ClassVar, Protocol

from core.exceptions import SupplierNotHavePricesError
from core.parse_paths import get_parse_paths
from parsers import data_provider
from parsers.base_item_actions.base_item_action import BaseItemAction
from parsers.base_item_actions.calc_percent_markup_item_action import (
    SetPercentMarkupItemAction,
)
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.row_item.row_item import RowItem
from parsers.xls_reader import IXlsReader, XlsReader

from . import price_markup
from .base_parser_config import ParseConfiguration, ParserParams
from .base_parser_row import _keep_row_item, drop_empty_rest, enrich_items
from .manufacturer_finder import ManufacturerFinder
from .markup_policy import IdentityMarkupPolicy, MarkupPolicy, make_markup_policy, percent_to_store
from .parse_statistic import ParseResultStatistic

type ItemActionClasses = list[type[BaseItemAction]]


class ParseConfigNotSetError(RuntimeError):
    """Raised when BaseParser.parse_config() is used before config is assigned."""

    def __init__(self) -> None:
        super().__init__("parse_config is not set")


class MarkupPolicyNotSetError(RuntimeError):
    """Raised when markup is used before MarkupPolicy is injected."""

    def __init__(self) -> None:
        super().__init__("markup_policy is not set")


class XlsReaderFactory(Protocol):
    """Класс-ридер с фабричным get_instance (XlsReader / FakeXlsReader)."""

    @classmethod
    def get_instance(cls, file_path: str, *args: Any, **kwargs: Any) -> IXlsReader: ...


class Parser(Protocol):
    """parser protocol"""

    @classmethod
    def supplier_folder_name(cls) -> str:
        """supplier folder name"""
        ...

    def get_parsed_items(self) -> list[RowItem]:
        """get parsed items"""
        ...

    def parse(self) -> list[RowItem]:
        """parse price files"""
        ...


class BaseParser:
    _item_actions: ClassVar[ItemActionClasses] = []
    _item_actions_after_process: ClassVar[ItemActionClasses] = [SetPercentMarkupItemAction]

    def __init__(
        self,
        parse_config: ParseConfiguration | None = None,
        file_prices: list[str] | None = None,
        xls_reader: type[XlsReaderFactory] = XlsReader,
        *,
        markup_policy: MarkupPolicy | None = None,
    ) -> None:
        self.parsed_items: list[RowItem] = []
        self._parse_config: ParseConfiguration | None = parse_config
        self.type_production: str | None = None
        self.xls_reader = xls_reader
        self.files: list[str] | None = file_prices
        self.logger = LoggerParseProcess(repr(self))
        self._black_list: list[str] | None = None
        self._stop_words: list[str] | None = None
        self._category_finder: CategoryFinder | None = None
        self._manufacturer_finder: ManufacturerFinder | None = None
        self.unknown_category_skips: list[str] = []
        self._markup_policy = markup_policy

    def parse_config(self) -> ParseConfiguration:
        if self._parse_config is None:
            raise ParseConfigNotSetError()
        return self._parse_config

    def markup_rules(self) -> data_provider.MarkupRules:
        return self.parse_config().get_markup_rules()

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

    def set_parse_config(self, parse_config: ParseConfiguration) -> None:
        self._parse_config = parse_config
        self._black_list = None
        self._stop_words = None
        self._manufacturer_finder = None

    def manufacturer_finder(self) -> ManufacturerFinder:
        if self._manufacturer_finder is None:
            aliases = self.parse_config().manufacturer_aliases()
            self._manufacturer_finder = ManufacturerFinder(aliases)
        return self._manufacturer_finder

    def parse(self) -> list[RowItem]:
        if not self.is_active:
            self.logger.log_disable_status()
            return []
        self._category_finder = CategoryFinder()
        self.files = self.files or get_file_prices(self)
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
        """drop empty rest → fill percent markup."""
        self.parsed_items = drop_empty_rest(self.parsed_items)
        self.fill_percent_markup(self.parsed_items)

    def read_rows(self, paths: list[str]) -> list[dict[str, Any]]:
        raw_rows: list[dict[str, Any]] = []
        for price_file in paths:
            self.type_production = _type_production_from_filename(price_file)
            raw_rows.extend(self.raw_parse(price_file))
        return raw_rows

    def map_items(self, raw_rows: list[dict[str, Any]]) -> list[RowItem]:
        return [self.parser_params().row_item_adaptor(row_item) for row_item in raw_rows]

    def enrich(self, row_items: list[RowItem]) -> list[RowItem]:
        return enrich_items(self, row_items)

    def filter_keep(self, row_items: list[RowItem]) -> list[RowItem]:
        return [row_item for row_item in row_items if _keep_row_item(self, row_item)]

    def apply_vendor_hooks(self, row_items: list[RowItem]) -> None:
        for row_item in row_items:
            self.process_parsed_row(row_item)

    def process_parsed_row(self, row_item: RowItem) -> None:
        """Хук после enrich: наценка, rest, категория. По умолчанию ничего."""

    def fill_percent_markup(self, row_items: list[RowItem]) -> None:
        for row_item in row_items:
            for item_action in self._item_actions_after_process:
                item_action(row_item).action()

    def correction_category(self, row_item: RowItem) -> None:
        if not row_item.type_production or self._category_finder is None:
            return
        category, bad_category = self._category_finder.find_in_str(row_item.type_production)
        if bad_category:
            row_item.type_production = category

    def get_markup_percent(self, price_value: float) -> float:
        return self._require_markup_policy().markup_percent_for_opt(price_value)

    def parser_params(self) -> ParserParams:
        return self.parse_config().parse_config.parser_params

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        supplier_name = self.parser_params().supplier.name
        sup_name = f"{class_name}: {supplier_name}"
        sheet_info = self.parser_params().sheet_info
        if sheet_info:
            sup_name = f"{sup_name} ({sheet_info})"
        return sup_name

    def get_parsed_items(self) -> list[RowItem]:
        return self.parsed_items

    @property
    def is_active(self) -> bool:
        return bool(self.get_current_vendor_config().enabled)

    @classmethod
    def replace_season(cls, row_item: RowItem) -> str | None:
        if not row_item.season:
            return None
        replaced_seasons = {"зима": "Зимняя", "лето": "Летняя"}
        return replaced_seasons.get(row_item.season.lower()) or row_item.season

    def raw_parse(self, full_file_xls_path: str) -> list[dict[str, Any]]:
        reader = self.get_xls_reader(full_file_xls_path)
        return reader.parse(self.parser_params().sheet_indexes)

    def get_xls_reader(self, full_file_xls_path: str) -> IXlsReader:
        return self.xls_reader.get_instance(
            full_file_xls_path,
            {
                "start_row": self.parser_params().start_row - 1,
                "columns": self.parser_params().columns,
            },
        )

    @classmethod
    def get_prepared_title(cls, row_item: RowItem) -> str:
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
        title_lower = title.lower()
        return any(s_word.lower() in title_lower for s_word in self.get_stop_words())

    def check_title_in_black_list(self, title: str) -> bool:
        return title in self.get_black_list()

    @classmethod
    def get_min_rest_count(cls) -> int:
        return 4

    @classmethod
    def get_item_rest(cls, row_item: RowItem) -> Any:
        return row_item.rest_count

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        if self.get_item_rest(row_item) < self.get_min_rest_count():
            row_item.rest_count = 0

    @classmethod
    def round_price(cls, price_value: float) -> float:
        """rounding to cents"""
        return math.ceil(price_value / 10) * 10

    @classmethod
    def is_category_row(cls, row_item: RowItem) -> bool:
        """is category row?"""
        return bool(row_item.title and not row_item.price_opt)

    def add_price_markup(self, row_item: RowItem) -> None:
        """calculate and fill price_markup field"""
        policy = self._require_markup_policy()
        opt = row_item.price_opt or 0
        price = policy.apply(opt, row_item.price_recommended)
        if isinstance(policy, IdentityMarkupPolicy):
            row_item.price_markup = price
        else:
            row_item.price_markup = self.round_price(price)
        percent = percent_to_store(policy, opt)
        if percent is not None:
            row_item.percent_markup = percent

    def _require_markup_policy(self) -> MarkupPolicy:
        if self._markup_policy is None:
            raise MarkupPolicyNotSetError()
        return self._markup_policy

    @classmethod
    def get_markup(cls, price: float, percent: float) -> float:
        """get price with absolute markup"""
        return price_markup.get_markup(price, percent)

    def get_current_vendor_config(self) -> data_provider.VendorParams:
        """get vendor configuration"""
        folder_name = self.parser_params().supplier.folder_name
        vendor = self.parse_config().all_vendor_config().get(folder_name)
        return vendor or data_provider.VendorParams(enabled=0)

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
        if row_item.spike.strip().lower() in ["ш.", "да"]:
            return "Да"
        return ""


class MarkupSkipCategoryParser(BaseParser):
    """Mim / FourTochki: наценка, min rest и категория после prepare."""

    def process_parsed_row(self, row_item: RowItem) -> None:
        self.add_price_markup(row_item)
        self.skip_by_min_rest(row_item)
        self.set_category(row_item)

    def set_category(self, row_item: RowItem) -> None:
        """Задать type_production. Override у листа поставщика."""


def make_parser[TParser: BaseParser](
    parser_cls: type[TParser],
    parse_config: ParseConfiguration,
    *,
    markup_policy: MarkupPolicy | None = None,
    file_prices: list[str] | None = None,
    xls_reader: type[XlsReaderFactory] = XlsReader,
) -> TParser:
    """Собрать парсер с политикой наценки. Не метод BaseParser."""
    policy = make_markup_policy(parse_config) if markup_policy is None else markup_policy
    return parser_cls(
        parse_config=parse_config,
        file_prices=file_prices,
        xls_reader=xls_reader,
        markup_policy=policy,
    )


def _type_production_from_filename(price_file: str) -> str:
    """Последний суффикс имени файла после `_` (например disks.xls)."""
    return price_file.rsplit("_", maxsplit=1)[-1]


def _glob_price_files(supplier_folder: Path, templates: list[str]) -> list[str]:
    """Собрать пути прайсов по glob-шаблонам."""
    list_files: list[str] = []
    for f_tmp in templates:
        list_files.extend(str(path) for path in supplier_folder.glob(f_tmp))
    return list_files


def get_file_prices(parser: BaseParser) -> list[str]:
    """get file prices"""
    prices_root = Path(get_parse_paths().file_prices_folder)
    supplier_folder = prices_root / parser.parser_params().supplier.folder_name
    list_files = _glob_price_files(supplier_folder, parser.parser_params().file_templates)

    if not list_files:
        supplier_name = parser.parser_params().supplier.name
        raise SupplierNotHavePricesError(f"Прайсов у поставщика ({supplier_name}) не обнаружено!")
    return list_files
