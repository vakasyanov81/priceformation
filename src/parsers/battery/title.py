"""Нормализация названия и выделение линейки из явного списка."""

from dataclasses import replace

from domain.battery.item import BatteryItem


def normalize_title(position: BatteryItem, lines: tuple[str, ...]) -> BatteryItem:
    """Сохранить слова названия; линейку искать целиком в начале с границей слова."""
    title = ' '.join((position.identity.title or '').split())
    matches = [line for line in lines if _matches(title, line)]
    if len(matches) != 1:
        raise ValueError(f'ожидается одна известная линейка, найдены {matches}: {title!r}')
    model = matches[0]
    declared = position.identity.model
    normalized_model = ' '.join((declared or '').split()).casefold()
    if declared is not None and normalized_model != model.casefold():
        raise ValueError(f'линейка {declared!r} не совпадает с названием {title!r}')
    return replace(position, identity=replace(position.identity, title=title, model=model))


def _matches(title: str, line: str) -> bool:
    normalized = title.casefold()
    expected = line.casefold()
    return normalized == expected or normalized.startswith(f'{expected} ')
