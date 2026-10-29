"""Сборка названия номенклатуры из параметров строки."""

from dataclasses import dataclass

from domain.row_item.row_item import RowItem
from parsers.nomenclature.brand import brand_label, model_label
from parsers.nomenclature.disk_labels import color_label, disk_diameter, disk_width, et_label
from parsers.nomenclature.labels import axis_label, layering_label, season_marks_label, xl_label


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
    xl: str = ''
    layering: object = ''
    camera: str = ''
    season_marks: tuple[str, ...] = ()
    axis: object = ''
    after_load: tuple[object, ...] = ()
    run_flat: str = ''

    def compose(self) -> str:
        """Порядок: размер, бренд, модель, нагрузка+скорость, XL, `<N>PR`, камерность, M+S, 3PMSF, RunFlat, ось."""
        return join_title_parts(
            self.size,
            self.brand,
            self.model,
            self.load_velocity,
            *self.after_load,
            self.xl,
            layering_label(self.layering),
            self.camera,
            *self.season_marks,
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
    """Название шины в каноническом порядке из полей позиции; камерность и ось задаёт вызывающий.

    ``XL``, ``M+S`` и ``3PMSF`` — свойства шины: берутся из названия поставщика и надписи на боковине.
    """
    source_title = row_item.identity.title
    sidewall = row_item.tire.inscription_on_the_side
    return TireTitleTokens(
        size,
        brand_label(row_item),
        model_label(row_item),
        load_velocity=load_velocity(row_item),
        xl=xl_label(source_title, sidewall),
        layering=row_item.tire.layering,
        camera=camera,
        season_marks=season_marks_label(source_title, sidewall),
        axis=axis,
        after_load=after_load,
        run_flat=run_flat,
    ).compose()


def compose_disk_title(row_item: RowItem, suffix: str = '') -> str:
    """Название диска в каноническом порядке из полей позиции.

    `<ширина>x<диаметр> <отверстия>x<PCD> ET<вылет> <DIA> <Цвет> <бренд> <модель> [хвост]`;
    ``suffix`` — хвост (толщина, усиление, завод и т. п.), который собирает вызывающий из названия поставщика.
    """
    return join_title_parts(
        join_size_parts(disk_width(row_item.tire.width), 'x', disk_diameter(row_item.tire.diameter)),
        join_size_parts(row_item.disk.slot_count, 'x', row_item.disk.pcd1),
        et_label(row_item.disk.eet),
        row_item.disk.central_diameter,
        color_label(row_item.disk.color),
        brand_label(row_item),
        model_label(row_item),
        suffix,
    )


def _nonempty_chunks(parts: tuple[object, ...]) -> list[str]:
    """Непустые куски после str/strip."""
    chunks: list[str] = []
    for part in parts:
        text = str(part or '').strip()
        if text:
            chunks.append(text)
    return chunks
