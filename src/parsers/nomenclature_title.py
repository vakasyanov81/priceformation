"""Сборка названия номенклатуры из параметров строки."""

from parsers.row_item.row_item import RowItem


def join_title_parts(*parts: object) -> str:
    """Склеить куски title пробелом, без пустых."""
    return " ".join(_nonempty_chunks(parts))


def join_size_parts(*parts: object) -> str:
    """Склеить куски размера без пробелов и пустых."""
    return "".join(_nonempty_chunks(parts))


def brand_label(row_item: RowItem) -> str:
    """Бренд для title."""
    return (row_item.manufacturer or "").lower().capitalize()


def load_velocity(row_item: RowItem) -> str:
    """Индекс нагрузки и скорости одним токеном."""
    load = row_item.index_load or ""
    velocity = row_item.index_velocity or ""
    return f"{load}{velocity}"


def compose_tire_title(row_item: RowItem, size: str, *extras: object) -> str:
    """Размер, бренд, модель и остальные поля шины."""
    return join_title_parts(
        size,
        brand_label(row_item),
        row_item.model,
        *extras,
    )


def _nonempty_chunks(parts: tuple[object, ...]) -> list[str]:
    """Непустые куски после str/strip."""
    chunks: list[str] = []
    for part in parts:
        text = str(part or "").strip()
        if text:
            chunks.append(text)
    return chunks
