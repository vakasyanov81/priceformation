"""Pipeline шагов разбора строки: порядок из стратегий или дефолтный."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.protocols import RowProcessorProtocol
from parsers.base_parser.row_enricher import RowEnricher
from parsers.base_parser.row_filters import RowFilters
from parsers.base_parser.strategy_hooks import StrategyHooks

# Порядок шагов без стратегий (обратная совместимость).
_DEFAULT_STEPS = ('min_rest', 'category', 'markup')


class RowPipeline:
    """Шаги обработки строки после enrich."""

    def __init__(
        self,
        hooks: StrategyHooks | None,
        row_filters: RowFilters,
        enricher: RowEnricher,
        row_processor: RowProcessorProtocol,
    ) -> None:
        self.hooks = hooks
        self.row_filters = row_filters
        self.enricher = enricher
        self.row_processor = row_processor

    def run(self, row_items: list[RowItem]) -> None:
        for row_item in row_items:
            self.process_row(row_item)

    def process_row(self, row_item: RowItem) -> None:
        """После enrich: pipeline из конфига или дефолтный порядок шагов.

        Производителя применяем ещё раз после pipeline: шаг ``title`` может
        собрать название заново из полей, и правку регистра бренда, сделанную
        в enrich, нужно наложить на финальный title (иначе ``TopTrust`` → ``Toptrust``).
        Поиск идёт всегда, даже если ``find_manufacturer_on_enrich`` выключен:
        так бренд из раздела-категории (Пионер) попадает в «Бренд».
        """
        if self.hooks is None:
            self._run_steps(_DEFAULT_STEPS, row_item)
            return
        self.row_filters.apply_warehouse_order(row_item)
        self._run_steps(self.hooks.pipeline, row_item)
        self.enricher.manufacturers.apply_manufacturer_after_pipeline(row_item)

    def _run_steps(self, steps: tuple[str, ...], row_item: RowItem) -> None:
        for step in steps:
            self._run_step(step, row_item)

    def _run_step(self, step: str, row_item: RowItem) -> None:
        """Один шаг pipeline; неизвестное имя шага пропускается."""
        if step == 'category':
            categories = self.enricher.categories
            categories.apply_category(row_item)
            categories.zero_rest_without_category(row_item)
            categories.apply_category_fields(row_item)
            return
        simple_steps = {
            'title': self.enricher.titles.set_prepared_title,
            'min_rest': self.row_filters.skip_by_min_rest,
            'markup': self.row_processor.add_price_markup,
        }
        run_simple = simple_steps.get(step)
        if run_simple is not None:
            run_simple(row_item)
