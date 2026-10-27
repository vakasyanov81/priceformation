"""Результат разбора и группировки прайсов."""

from dataclasses import dataclass, field

from domain.row_item.row_item import RowItem

type UnknownCategorySkip = tuple[str, str]


@dataclass
class ParseResult:
    """Результат разбора и группировки: записи и накопленные пропуски."""

    parsed_items: list[RowItem] = field(default_factory=list)
    unknown_category_skips: list[UnknownCategorySkip] = field(default_factory=list)
    black_list_skips: int = 0
    type_corrections: int = 0
    title_conflicts: int = 0
    titles_not_composed: int = 0
    homoglyph_fixes: int = 0
    homoglyph_suspects: int = 0
