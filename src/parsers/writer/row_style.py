"""
цвета строк и легенда цветов для xlsx-шаблонов
"""

from typing import Any

from parsers.writer.ixlsx_driver import IXlsDriver

type RowColor = tuple[str | None, int | None]
type PriceRow = dict[str, Any]


def write_legend(driver: IXlsDriver, legend: list[tuple[str, str]]) -> int:
    """Легенда цветов над шапкой: образец цвета в первой ячейке, пояснение во второй.

    Возвращает число строк, на которое сдвигаются шапка и данные (легенда и пустая строка-отступ).
    """
    if not legend:
        return 0
    for row_index, (color, text) in enumerate(legend):
        driver.write(row_index, 0, None, _color=color)
        driver.write(row_index, 1, text)
    return len(legend) + 1


def _rule_color(product: PriceRow, colors: dict[str, Any]) -> RowColor:
    """цвет по одному правилу by_column/with_map"""
    column_name = colors.get('by_column')
    column_value = product.get(column_name) if column_name else None
    color_map = colors.get('with_map')
    if not column_value or not color_map:
        return None, None
    return color_map.get(column_value), colors.get('set_to_column_index')


def row_color(colors: dict[str, Any], product: PriceRow) -> RowColor:
    """Цвет строки: либо одно правило, либо `rules` — первое сработавшее."""
    rules = colors.get('rules')
    if rules is None:
        return _rule_color(product, colors)
    for rule in rules:
        color = _rule_color(product, rule)
        if color[0]:
            return color
    return None, None
