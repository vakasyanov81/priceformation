"""Сборка названия камеры и ободной ленты."""

from parsers.nomenclature_title import join_size_parts, join_title_parts


def tube_size_label(width: str, height_percent: str, diameter: str, ext_diameter: str, width_max: str = '') -> str:
    """Размер камеры или ленты: `11.00-20`, `12.5/80-18`, `175/185-16`, `1200x500-508`."""
    if ext_diameter:
        return join_size_parts(ext_diameter, 'x', width, '-', diameter)
    second = height_percent or width_max
    return join_size_parts(width, '/' if second else '', second, '-', diameter)


def compose_tube_title(is_rim_tape: bool, size: str, brand: str = '', model: str = '', *, valve: bool = False) -> str:
    """Название камеры или ободной ленты: `<Камера|Ободная лента> <размер> [бренд] [модель] [с вентилем]`.

    ``model`` — модель камеры (`ГК-145`) или ленты (`300-508А`); модель ленты уже содержит размер
    и ставится вместо него.
    """
    if is_rim_tape:
        return join_title_parts('Ободная лента', model or size, brand, 'с вентилем' if valve else '')
    return join_title_parts('Камера', size, brand, model, 'с вентилем' if valve else '')
