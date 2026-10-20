"""Каноническое написание токенов названия диска: ширина, диаметр, `ET`, цвет."""


def et_label(eet: object) -> str:
    """ET с нулём: 0 не должен пропадать как falsy."""
    if eet is None or eet == '':
        return 'ET'
    return f'ET{eet}'


def disk_diameter(raw: object) -> str:
    """Диаметр диска без хвостового .0, без порчи 22.5."""
    text = str(raw or '')
    if text.endswith('.0'):
        return text[:-2]
    return text


def disk_width(raw: object) -> str:
    """Ширина диска с десятичной частью, как в прайсе: `7` → `7.0`, `6.75` без изменений."""
    text = str(raw or '')
    return f'{text}.0' if text.isdigit() else text


def color_label(raw: object) -> str:
    """Цвет диска с заглавной буквы, остальное как есть: `графит` → `Графит`, `Хай вэй` и `BL` не меняются."""
    color = str(raw or '').strip()
    return color[:1].upper() + color[1:]
