"""
logic for zapaska (rest) vendor
"""

from typing import Any

from parsers.base_parser.base_parser import BaseParser, ReaderFactory
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
    make_parse_config,
)
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.data_provider.title_aliases import load_title_aliases
from parsers.json_reader import JsonPriceReader
from parsers.row_item.row_item import RowItem

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

zapaska_config = make_parse_config(zapaska_params)


class ZapaskaDiskJSON(BaseParser):
    """
    Parser rest and price opt for zapaska vendor
    """

    _type_production = "Диск"

    def __init__(
        self,
        parse_config: ParseConfiguration,
        file_prices: list[Any] | None = None,
        data_reader: type[ReaderFactory] = JsonPriceReader,
        *,
        markup_policy: MarkupPolicy | None = None,
    ) -> None:
        """init"""
        self.not_matched_position: list[str] = []
        self.title_aliases = load_title_aliases(parse_config.parse_config.parser_params.supplier.name)
        super().__init__(parse_config, file_prices, data_reader, markup_policy=markup_policy)

    def category_for(self, row_item: RowItem) -> str | None:
        return self._type_production

    def apply_category(self, row_item: RowItem) -> None:
        super().apply_category(row_item)
        if not row_item.type_production:
            row_item.rest_count = 0

    @classmethod
    def get_item_rest(cls, row_item: RowItem) -> int:
        """get rest count"""
        return row_item.rest_count

    def get_prepared_title(self, row_item: RowItem) -> str:
        """Normalize title spaces and apply title aliases."""
        chunks = []
        for chunk in row_item.title.split(" "):
            stripped = chunk.strip()
            if stripped:
                chunks.append(stripped)
        title = " ".join(chunks)
        return self.title_aliases.get(title) or title

    def add_price_markup(self, row_item: RowItem) -> None:
        """Отпускная по MarkupPolicy; пустой закуп не трогает строку."""
        price_recommended = row_item.price_recommended or 0
        price_opt = row_item.price_opt

        if not price_opt:
            return

        if not price_recommended:
            self.not_matched_position.append(row_item.title)

        price_with_markup = self._require_markup_policy().apply(price_opt, row_item.price_recommended)
        row_item.price_markup = self.round_price(price_with_markup) if price_with_markup else None
