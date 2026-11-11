"""Общие счётчики групп и отдельная диагностика шин и дисков."""

from dataclasses import dataclass, field

from parsers.base_parser.parse_statistic import ParserStats

type UnknownCategorySkip = tuple[str, str]


@dataclass
class GroupStatistics:
    """Счётчики, смысл которых не зависит от модели позиции."""

    item_count: int = 0
    priced_items: int = 0
    doubles: int = 0
    black_list_skips: int = 0


@dataclass
class TireAndDiskDiagnostics:
    """Шинные счётчики не являются характеристиками других товарных групп."""

    type_corrections: int = 0
    title_conflicts: int = 0
    titles_not_composed: int = 0
    homoglyph_fixes: int = 0
    homoglyph_suspects: int = 0
    unknown_category_skips: list[UnknownCategorySkip] = field(default_factory=list)

    def accumulate(self, stats: ParserStats, skips: list[UnknownCategorySkip]) -> None:
        """Сохранить независимую копию диагностики следующей секции."""
        self.unknown_category_skips.extend(skips)
        self.type_corrections += stats.type_corrections
        self.title_conflicts += stats.title_conflicts
        self.titles_not_composed += stats.titles_not_composed
        self.homoglyph_fixes += stats.homoglyph_fixes
        self.homoglyph_suspects += stats.homoglyph_suspects
