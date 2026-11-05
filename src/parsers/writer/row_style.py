"""
цвета строк и легенда цветов для xlsx-шаблонов
"""

from typing import Any

from parsers.writer.ixlsx_driver import IXlsDriver

type RowColor = tuple[str, int | None]
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


def _rule_color(product: PriceRow, colors: dict[str, Any]) -> RowColor | None:
    """цвет по одному правилу by_column/with_map; None — правило к строке не подходит"""
    column_name = colors.get('by_column')
    column_value = product.get(column_name) if column_name else None
    color_map = colors.get('with_map')
    if not column_value or not color_map:
        return None
    color = color_map.get(column_value)
    return (color, colors.get('set_to_column_index')) if color else None


def row_colors(colors: dict[str, Any], product: PriceRow) -> list[RowColor]:
    """Цвета строки по порядку правил (либо одно правило, либо `rules`); приоритет у более раннего."""
    rules = colors.get('rules') or [colors]
    matched = (_rule_color(product, rule) for rule in rules)
    return [color for color in matched if color]


def cell_color(colors: list[RowColor], col_index: int) -> str | None:
    """Цвет ячейки: первое правило, которое красит всю строку (индекс None) или эту колонку."""
    for color, color_index in colors:
        if color_index in {None, col_index}:
            return color
    return None
