from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.price_markup import calc_percent, get_markup
from parsers.data_provider.markup_rules import (
    ABSOLUTE_MODE_DELTA,
    MarkUpParams,
    MarkupRules,
)


class MarkupPolicy:
    def __init__(
        self,
        rules: MarkupRules,
        price_map: tuple[MarkUpParams, ...],
    ) -> None:
        self._rules = rules
        self._price_map = price_map

    def markup_percent_for_opt(self, price_opt: float) -> float:
        """Рассчитать процент наценки по оптовой цене"""
        default_percent = min({price_rule.percent_markup for price_rule in self._price_map} or (0,))

        if not price_opt:
            return default_percent

        for price_rule in self._price_map:
            if price_rule.min <= price_opt <= price_rule.max:
                return price_rule.percent_markup

        return default_percent

    def apply(self, price_opt: float, price_recommended: float | None) -> float:
        """Отпускная цена до округления (шаги 1–4 базового алгоритма)."""
        price = price_recommended or 0
        opt = price_opt or 0

        if self._rules.should_replace_with_map(
            price_recommended,
            self._is_small_recommended_percent(opt, price_recommended),
        ):
            price = get_markup(opt, self.markup_percent_for_opt(opt))

        if self._is_big_recommended_percent(opt, price_recommended) and not price_recommended:
            price = get_markup(opt, self._rules.max_recommended_percent_markup)

        if self._is_small_absolute_markup(price, opt):
            price = self._price_with_absolute_rule(opt)

        return price

    def _is_small_recommended_percent(self, price_opt: float, price_recommended: float | None) -> bool:
        """Проверка, что процент наценки по МРЦ укладывается в минимальный процент наценки из настроек"""
        return recommended_percent(price_opt, price_recommended) < self._rules.min_recommended_percent_markup

    def _is_big_recommended_percent(self, price_opt: float, price_recommended: float | None) -> bool:
        """Процент РРЦ больше max; выключено, если max_recommended_percent_markup == 0."""
        if not self._rules.max_recommended_percent_markup:
            return False
        return recommended_percent(price_opt, price_recommended) > self._rules.max_recommended_percent_markup

    def _is_small_absolute_markup(self, selling_price: float, purchase_price: float) -> bool:
        """Отпускная минус закуп меньше абсолютного пола."""
        margin = selling_price - purchase_price
        floor = self._rules.absolute_markup_rules.min_absolute_markup
        if self._rules.absolute_markup_rules.mode == ABSOLUTE_MODE_DELTA:
            return margin <= floor
        return margin < floor

    def _price_with_absolute_rule(self, price_opt: float) -> float:
        """Цена по абсолютному правилу: множитель или дельта к закупу."""
        absolute = self._rules.absolute_markup_rules
        if absolute.mode == ABSOLUTE_MODE_DELTA:
            return price_opt + absolute.min_absolute_markup
        return price_opt * absolute.markup_percent


class IdentityMarkupPolicy(MarkupPolicy):
    @classmethod
    def create(cls) -> IdentityMarkupPolicy:
        """Политика «без наценки». JSON не читает."""
        return cls(MarkupRules(markup_rules={}), ())

    def apply(self, price_opt: float, price_recommended: float | None) -> float:
        """Отпускная = закуп. Внутренний склад: цена уже с наценкой, JSON не нужен."""
        return price_opt or 0


class MapOnOptMarkupPolicy(MarkupPolicy):
    def apply(self, price_opt: float, price_recommended: float | None) -> float:
        """Отпускная до округления: только карта % на закуп. РРЦ и absolute игнорируются."""
        opt = price_opt or 0
        return get_markup(opt, self.markup_percent_for_opt(opt))

    def stored_percent_markup(self, price_opt: float) -> float:
        """map% * 100 до округления цены — как сейчас пишут Poshk/Pioner."""
        return self.markup_percent_for_opt(price_opt or 0) * 100


def percent_to_store(policy: MarkupPolicy, price_opt: float) -> float | None:
    """Процент для записи в строку. None — пусть посчитает SetPercentMarkupItemAction."""
    if isinstance(policy, MapOnOptMarkupPolicy):
        return policy.stored_percent_markup(price_opt)
    return None


def recommended_percent(
    price_opt: float,
    price_recommended: float | None,
) -> float:
    recommended = price_recommended or 0
    opt = price_opt or 0
    return calc_percent(recommended, opt) if recommended else 0


def make_markup_policy(parse_config: ParseConfiguration) -> MarkupPolicy:
    """Собрать политику из правил и карты % конфига. Не метод парсера."""
    return MarkupPolicy(
        rules=parse_config.get_markup_rules(),
        price_map=parse_config.get_price_markup_map(),
    )


def make_map_on_opt_markup_policy(parse_config: ParseConfiguration) -> MapOnOptMarkupPolicy:
    """Собрать политику «карта % на закуп» из конфига. Не метод парсера."""
    return MapOnOptMarkupPolicy(
        rules=parse_config.get_markup_rules(),
        price_map=parse_config.get_price_markup_map(),
    )
