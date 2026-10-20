"""Сборка названия номенклатуры из параметров строки."""

from dataclasses import dataclass

from domain.row_item.row_item import RowItem
from parsers.nomenclature_brand import brand_label, model_label
from parsers.nomenclature_labels import axis_label, layering_label


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


@dataclass(frozen=True, slots=True)
class TireTitleTokens:
    """Токены названия шины; порядок задаёт ``compose``, пустые пропускаются."""

    size: str
    brand: str
    model: str
    load_velocity: str = ''
    layering: object = ''
    camera: str = ''
    axis: object = ''
    after_load: tuple[object, ...] = ()
    run_flat: str = ''

    def compose(self) -> str:
        """Единый порядок: размер, бренд, модель, нагрузка+скорость, `<N>PR`, камерность, RunFlat, ось."""
        return join_title_parts(
            self.size,
            self.brand,
            self.model,
            self.load_velocity,
            *self.after_load,
            layering_label(self.layering),
            self.camera,
            self.run_flat,
            axis_label(self.axis),
        )


def compose_tire_title(
    row_item: RowItem,
    size: str,
    *,
    camera: str = '',
    axis: str = '',
    after_load: tuple[object, ...] = (),
    run_flat: str = '',
) -> str:
    """Название шины в каноническом порядке из полей позиции; камерность и ось задаёт вызывающий."""
    return TireTitleTokens(
        size,
        brand_label(row_item),
        model_label(row_item),
        load_velocity=load_velocity(row_item),
        layering=row_item.tire.layering,
        camera=camera,
        axis=axis,
        after_load=after_load,
        run_flat=run_flat,
    ).compose()


def _nonempty_chunks(parts: tuple[object, ...]) -> list[str]:
    """Непустые куски после str/strip."""
    chunks: list[str] = []
    for part in parts:
        text = str(part or '').strip()
        if text:
            chunks.append(text)
    return chunks
