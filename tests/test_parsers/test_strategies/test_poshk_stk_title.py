"""Стратегия слота `title` для Пошка и STK: сборка названия шины в каноническом порядке."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.poshk_stk_title import PoshkStkTireCompose
from parsers.strategies.protocols import BrandProbe

_FALLBACK_BRAND = 'Алтайшина'


_CAMERA_BY_KIND = {
    'автошина': 'TT',
    'спецшина': 'TT',
    'сельхозшина': 'TT',
    'автопокрышка': 'TL',
    'спецпокрышка': 'TL',
    'сельхозпокрышка': 'TL',
}


def _strategy(fallback_brand: str = '', brand_probe: BrandProbe | None = None) -> PoshkStkTireCompose:
    return PoshkStkTireCompose(fallback_brand, brand_probe)


def _camera_strategy() -> PoshkStkTireCompose:
    return PoshkStkTireCompose('', None, _CAMERA_BY_KIND)


class _Probe:
    """Детектор бренда с заданным ответом и журналом проверенных названий."""

    def __init__(self, *, has_brand: bool) -> None:
        self.has_brand = has_brand
        self.titles: list[str | None] = []

    def __call__(self, title: str | None) -> bool:
        self.titles.append(title)
        return self.has_brand


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        (
            '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт',
            '10.00R20 DOUBLEROAD DR-801 149/146K 18PR Универсальная',
        ),
        (
            '11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, (1 шт)',
            '11R22.5 TAITONG HS103 146/143M 16PR Ведущая',
        ),
        (
            '11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт',
            '11.00R20 НКШЗ И-68А 150/146K 16PR',
        ),
        (
            '12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт',
            '12.4L-16 БШК Бел-160М 111A6 8PR',
        ),
        (
            'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка',
            '11R22.5 GREENSTONE DR668 146/143L 16PR',
        ),
        (
            'Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал',
            '235/75R17.5 LingLong LLA78 143/141J 18PR TL',
        ),
        (
            'Автошина 7.00 R16LT14PR 118/114L GREENSTONE ST896 змейка',
            '7.00R16LT GREENSTONE ST896 118/114L 14PR',
        ),
    ],
)
def test_glues_in_canonical_order(raw: str, expected: str) -> None:
    """Пошк и STK: параметры пересобираются в канонический порядок, из назначения остаётся только ось."""
    assert _strategy().prepare(RowItem({'title': raw})) == expected


def test_uses_manufacturer_for_brand() -> None:
    """Канонический производитель подставляется на место разобранного бренда."""
    row = RowItem(
        {
            'title': '11R22.5 GREENSTONE DR668 146/143L 16PR',
            'manufacturer_name': 'GreenStone',
        },
    )

    assert _strategy().prepare(row) == '11R22.5 GreenStone DR668 146/143L 16PR'


def test_is_idempotent() -> None:
    """Повторная сборка уже собранного названия не меняет результат."""
    strategy = _strategy()
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт'})

    once = strategy.prepare(row)
    twice = strategy.prepare(row)

    assert once == twice == '10.00R20 DOUBLEROAD DR-801 149/146K 18PR Универсальная'


@pytest.mark.parametrize('axis', ['Универсальная', 'Ведущая', 'Рулевая', 'Прицепная', 'Карьерная'])
def test_recompose_keeps_canonical_axis_at_end(axis: str) -> None:
    """Название собирается дважды (при обогащении и в шаге pipeline): каноническая ось не уходит в модель."""
    strategy = _strategy()
    first = strategy.prepare(RowItem({'title': f'10.00 R20 Double Road DR-801 н.с.18 149/146K TT {axis}'}))

    assert first == f'10.00R20 Double Road DR-801 149/146K 18PR TT {axis}'
    assert strategy.prepare(RowItem({'title': first})) == first


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        (
            'Диск штамп NORTEC-16 11.75*22.5 10*335 ET0 d281 , шт',
            'Диск штамп NORTEC-16 11.75x22.5 10x335 ET0 d281',
        ),
        (
            'Диск стальной YONGZHENG 22,5*11,75 10 26мм ЕТ0 D281 раст.335 (16мм)',
            'Диск стальной YONGZHENG 22.5x11.75 10 26мм ЕТ0 D281 раст.335 (16мм)',
        ),
    ],
    ids=['poshk', 'stk'],
)
def test_falls_back_to_normalize_for_disk(raw: str, expected: str) -> None:
    """Диск не размер шины: работает обычная нормализация размера."""
    assert _strategy().prepare(RowItem({'title': raw})) == expected


def test_empty_title_stays_empty() -> None:
    """Пустой title не превращается в заглушку."""
    assert _strategy().prepare(RowItem({})) == ''


def test_ship_without_brand_uses_fallback_brand() -> None:
    """Ведущая «Шина» без бренда отдаётся нормализации с брендом-заглушкой."""
    title = 'Шина 11.00R20 И-111А 16PR 150/146K TT, шт'
    probe = _Probe(has_brand=False)

    prepared = _strategy(_FALLBACK_BRAND, probe).prepare(RowItem({'title': title}))

    assert prepared == 'Алтайшина 11.00R20 И-111А 16PR 150/146K TT'
    assert title in probe.titles


def test_ship_with_brand_is_composed() -> None:
    """Ведущая «Шина» с известным брендом разбирается и пересобирается."""
    strategy = _strategy(_FALLBACK_BRAND, _Probe(has_brand=True))

    prepared = strategy.prepare(RowItem({'title': 'Шина 10.00R20 FORWARD Traction-310 16PR 146/143K TT, шт'}))

    assert prepared == '10.00R20 FORWARD Traction-310 146/143K 16PR TT'


@pytest.mark.parametrize(
    ('fallback_brand', 'probe'),
    [('', _Probe(has_brand=False)), (_FALLBACK_BRAND, None)],
    ids=['no-fallback-brand', 'no-probe'],
)
def test_ship_composed_without_fallback_setup(fallback_brand: str, probe: _Probe | None) -> None:
    """Без бренда-заглушки или детектора «Шина» тоже разбирается — подставлять нечего."""
    strategy = _strategy(fallback_brand, probe)

    prepared = strategy.prepare(RowItem({'title': 'Шина 11.00R20 И-111А 16PR 150/146K TT, шт'}))

    assert prepared == '11.00R20 И-111А 150/146K 16PR TT'


def test_no_ship_ignores_probe() -> None:
    """Без ведущей «Шина» детектор бренда не спрашивается."""
    probe = _Probe(has_brand=False)

    prepared = _strategy(_FALLBACK_BRAND, probe).prepare(RowItem({'title': '11.00 R20 И-68А н.с. 16 150/146K НКШЗ'}))

    assert prepared == '11.00R20 НКШЗ И-68А 150/146K 16PR'
    assert not probe.titles


def test_fallback_normalize_gets_probe() -> None:
    """Нормализация (не размер шины) тоже видит детектор: с брендом заглушка не нужна."""
    strategy = _strategy(_FALLBACK_BRAND, _Probe(has_brand=True))

    prepared = strategy.prepare(RowItem({'title': 'Шина Камера 12.5/80-18 TT, шт'}))

    assert prepared == 'Камера 12.5/80-18 TT'


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт', '11.00R20 НКШЗ И-68А 150/146K 16PR TT'),
        ('10.00-20 NEXT G2/L2 н.с.18 с об/л спецшина, шт', '10.00-20 NEXT G2/L2 18PR TT'),
        ('12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт', '12.4L-16 БШК Бел-160М 111A6 8PR TT'),
        (
            '11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, шт',
            '11R22.5 TAITONG HS103 146/143M 16PR TL Ведущая',
        ),
        ('10-16.5 NEXT SKS-3 н.с.12 спецпокрышка, шт', '10-16.5 NEXT SKS-3 12PR TL'),
        ('12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозпокрышка, шт', '12.4L-16 БШК Бел-160М 111A6 8PR TL'),
    ],
)
def test_camera_added_by_kind_word(raw: str, expected: str) -> None:
    """Нет камерности в названии — её даёт слово вида шины: *шина → TT, *покрышка → TL."""
    assert _camera_strategy().prepare(RowItem({'title': raw})) == expected


def test_camera_from_title_wins_over_kind_word() -> None:
    """Камерность, уже указанная в названии, не перетирается видом шины."""
    prepared = _camera_strategy().prepare(RowItem({'title': 'а/п 425/85R21 NORTEC TR-184-1 18PR 156J TL автошина, шт'}))

    assert prepared == '425/85R21 NORTEC TR-184-1 156J 18PR TL'


def test_camera_not_added_without_kind_word() -> None:
    """Слова вида нет — камерность не выдумываем."""
    prepared = _camera_strategy().prepare(RowItem({'title': '17.5-25 Rockbuster H108A E3/L3 н.с.28'}))

    assert prepared == '17.5-25 Rockbuster H108A E3/L3 28PR'


def test_camera_not_added_without_config() -> None:
    """Без `camera_by_kind` (STK) поведение прежнее."""
    prepared = _strategy().prepare(RowItem({'title': '11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт'}))

    assert prepared == '11.00R20 НКШЗ И-68А 150/146K 16PR'
