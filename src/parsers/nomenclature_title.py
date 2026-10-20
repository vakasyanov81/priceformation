"""Сборка названия номенклатуры из параметров строки."""

from domain.row_item.row_item import RowItem
from parsers.nomenclature_brand import brand_label, model_label


def join_title_parts(*parts: object) -> str:
    """Склеить куски title пробелом, без пустых."""
    return ' '.join(_nonempty_chunks(parts))


def join_size_parts(*parts: object) -> str:
    """Склеить куски размера без пробелов и пустых."""
    return ''.join(_nonempty_chunks(parts))


def load_velocity(row_item: RowItem) -> str:
    """Индекс нагрузки и скорости одним токеном."""
    load = row_item.tire.index_load or ''
    velocity = row_item.tire.index_velocity or ''
    return f'{load}{velocity}'


def compose_tire_title(row_item: RowItem, size: str, *extras: object) -> str:
    """Размер, бренд, модель и остальные поля шины."""
    return join_title_parts(
        size,
        brand_label(row_item),
        model_label(row_item),
        *extras,
    )


def _nonempty_chunks(parts: tuple[object, ...]) -> list[str]:
    """Непустые куски после str/strip."""
    chunks: list[str] = []
    for part in parts:
        text = str(part or '').strip()
        if text:
            chunks.append(text)
    return chunks
