"""
logic for zapaska (rest) vendor
"""

import json
from pathlib import Path
from typing import Any, cast

from cfg.main import MainConfig
from core.file_reader import read_file
from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser, XlsReaderFactory
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_disk_markup import make_price_markup_value
from parsers.xls_reader import XlsReader

type JsonRow = dict[str, Any]
type JsonRows = list[JsonRow]
type ColumnMap = dict[str, str]

column_mapping = {
    "cae": RowItem.code_art.name,
    "rest": RowItem.rest_count.name,
    "price": RowItem.price_opt.name,
    "retail": RowItem.price_recommended.name,
    "diam_center": RowItem.central_diameter.name,
    "holes": RowItem.slot_count.name,
    "diam_holes": RowItem.pcd1.name,
    "ET": RowItem.eet.name,
    "brand": RowItem.manufacturer.name,
    "name": RowItem.title.name,
    "category": RowItem.type_production.name,
}

zapaska_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="zapaska", name="Запаска (диски)", code="2"),
    start_row=0,
    sheet_info="",
    columns=column_mapping,
    stop_words=[],
    file_templates=["disk.json"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(zapaska_params.supplier.folder_name)


def get_title_aliases(supplier_name: str) -> dict[str, Any]:
    """Load title aliases for supplier from user config."""
    try:
        return _load_title_aliases(supplier_name)
    except FileNotFoundError:
        return {}


def _load_title_aliases(supplier_name: str) -> dict[str, Any]:
    """Read title aliases JSON and invert map for supplier."""
    raw = json.loads(read_file(MainConfig().title_aliases_file_path)) or {}
    return invert_map(raw.get(supplier_name) or {})


def invert_map(title_aliases: dict[str, Any]) -> dict[str, Any]:
    """Invert {correct: [incorrect, ...]} to {incorrect: correct}."""
    inverted = {}
    for correct_title, incorrect_titles in title_aliases.items():
        for incorrect_title in incorrect_titles:
            inverted[incorrect_title] = correct_title
    return inverted


def rename_fields(rows: JsonRows, columns: ColumnMap) -> None:
    """Rename JSON keys to RowItem field names."""
    for row in rows:
        for source_key, target_key in columns.items():
            if source_key in row:
                row[target_key] = row.pop(source_key)


zapaska_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=zapaska_params,
    )
)


class ZapaskaDiskJSON(BaseParser):
    """
    Parser rest and price opt for zapaska vendor
    """

    _type_production = "Диск"

    def __init__(
        self,
        parse_config: ParseConfiguration,
        file_prices: list[Any] | None = None,
        xls_reader: type[XlsReaderFactory] = XlsReader,
        *,
        markup_policy: MarkupPolicy | None = None,
    ) -> None:
        """init"""
        self.not_matched_position: list[str] = []
        self.title_aliases = get_title_aliases(parse_config.parse_config.parser_params.supplier.name)
        super().__init__(parse_config, file_prices, xls_reader, markup_policy=markup_policy)

    def raw_parse(self, full_file_xls_path: str) -> list[dict[str, Any]]:
        """raw parse"""
        with Path(full_file_xls_path).open(encoding="utf-8") as out_file:
            text_data = out_file.read()
        loaded = json.loads(text_data)
        dictable_data = cast(list[dict[str, Any]], loaded)
        parser_params = self.parse_config().parse_config.parser_params
        rename_fields(dictable_data, cast(dict[str, str], parser_params.columns))
        return dictable_data

    def process_parsed_row(self, row_item: RowItem) -> None:
        self.make_price_markup(row_item)
        self.skip_by_min_rest(row_item)
        row_item.type_production = self.get_type_production(row_item)
        if not row_item.type_production:
            row_item.rest_count = 0

    def get_type_production(self, row_item: RowItem) -> str:
        """Return fixed type production for disk prices."""
        return self._type_production

    @classmethod
    def get_item_rest(cls, row_item: RowItem) -> int:
        """get rest count"""
        return row_item.rest_count

    def get_prepared_title(self, row_item: RowItem) -> str:  # type: ignore[override]
        """Normalize title spaces and apply title aliases."""
        chunks = []
        for chunk in row_item.title.split(" "):
            stripped = chunk.strip()
            if stripped:
                chunks.append(stripped)
        title = " ".join(chunks)
        return self.title_aliases.get(title) or title

    def make_price_markup(self, row_item: RowItem) -> None:
        """set markup
        цена закупа от 0 до 5000 прибавляем наценку 17%
        цена закупа от 5000 до 10000 прибавляем наценку 15%
        цена закупа от 10000 до 15000 прибавляем наценку 13%
        цена закупа от 15000 до 20000 прибавляем наценку 10%
        """

        price_recommended = row_item.price_recommended or 0
        price_opt = row_item.price_opt

        if not price_opt:
            return

        if not price_recommended:
            self.not_matched_position.append(row_item.title)

        price_with_markup = make_price_markup_value(price_recommended, price_opt)
        row_item.price_markup = self.round_price(price_with_markup) if price_with_markup else None
