"""Pipeline шагов разбора строки в BaseParser: порядок из стратегий или дефолтный."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.parser_markup import ParserMarkup
from parsers.base_parser.strategy_hooks import StrategyHooks


class ParserPipeline(ParserMarkup):
    """Шаги обработки строки после enrich."""

    def apply_vendor_hooks(self, row_items: list[RowItem]) -> None:
        for row_item in row_items:
            self.process_parsed_row(row_item)

    def process_parsed_row(self, row_item: RowItem) -> None:
        """После enrich: pipeline из конфига или дефолтный порядок шагов.

        Производителя применяем ещё раз после pipeline: шаг ``title`` может
        собрать название заново из полей, и правку регистра бренда, сделанную
        в enrich, нужно наложить на финальный title (иначе ``TopTrust`` → ``Toptrust``).
        Поиск идёт всегда, даже если ``find_manufacturer_on_enrich`` выключен:
        так бренд из раздела-категории (Пионер) попадает в «Бренд».
        """
        hooks = self._strategy_hooks
        if hooks is not None:
            self._run_pipeline(hooks, row_item)
            self.apply_manufacturer_after_pipeline(row_item)
            return
        # дефолтный порядок (обратная совместимость)
        self.after_row_mapped(row_item)
        self.row_filters.skip_by_min_rest(row_item)
        self.categories.apply_category(row_item)
        self.add_price_markup(row_item)

    def _run_pipeline(self, hooks: StrategyHooks, row_item: RowItem) -> None:
        """Выполнить шаги pipeline по порядку."""
        self.row_filters.apply_warehouse_order(row_item)
        for step in hooks.pipeline:
            self._run_step(step, row_item)

    def _run_step(self, step: str, row_item: RowItem) -> None:
        """Один шаг pipeline; неизвестное имя шага пропускается."""
        if step == 'category':
            self.categories.apply_category(row_item)
            self.categories.zero_rest_without_category(row_item)
            self.categories.apply_category_fields(row_item)
            return
        simple_steps = {
            'title': self.titles.set_prepared_title,
            'min_rest': self.row_filters.skip_by_min_rest,
            'markup': self.add_price_markup,
        }
        run_simple = simple_steps.get(step)
        if run_simple is not None:
            run_simple(row_item)

    def after_row_mapped(self, row_item: RowItem) -> None:
        """Редкое уникальное после enrich (title, fill_from_title). По умолчанию ничего."""
