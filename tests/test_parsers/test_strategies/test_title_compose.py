"""Обёртка `title.compose`: название шины из полей позиции в каноническом порядке."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.normalize import NormalizeTitle
from parsers.strategies.title_compose import TireTitleFromFields, titles_not_composed_message
from parsers.strategies.title_params import ParamsFromTitle
from parsers.strategies.title_registry import make_title_strategy
from parsers.vendor_config.slot_configs import TitleConfig

_ALIASES = {'ikon (nokian tyres)': 'Nokian', 'nordman': 'Nordman', 'gislaved': 'Gislaved', 'cordiant': 'Cordiant'}


def _probe(title: str | None) -> str | None:
    """Производитель по алиасам: самое позднее найденное слово из таблицы, как у поиска по названию."""
    lower = (title or '').lower()
    found = {lower.rfind(alias): name for alias, name in _ALIASES.items()}
    return found[max(found)] if max(found) >= 0 else None


def _compose(row: RowItem) -> str | None:
    return TireTitleFromFields(ParamsFromTitle(NormalizeTitle()), _probe).prepare(row)


@pytest.mark.parametrize(
    ('fields', 'expected'),
    [
        pytest.param(
            {
                'title': '205/50R17 Kumho WinterCraft Ice WI32 93 T XL шип',
                'manufacturer_name': 'Kumho',
                'model': 'WinterCraft Ice WI32',
                'index_load': '93',
                'index_velocity': 'T',
            },
            '205/50R17 Kumho WinterCraft Ice WI32 93T XL',
            id='zapaska-load-and-speed-in-columns-spike-dropped',
        ),
        pytest.param(
            {
                'title': '255/35R19 Ikon (Nokian Tyres) Autograph Ice 9 96T XL шип',
                'manufacturer_name': 'Ikon (Nokian Tyres)',
                'model': 'Autograph Ice 9',
            },
            '255/35R19 Nokian Autograph Ice 9 96T XL',
            id='zapaska-owner-in-brackets-replaced-by-manufacturer',
        ),
        pytest.param(
            {'title': '275/45R20 Gislaved ArcticControl 110T XL FR', 'model': 'ArcticControl'},
            '275/45R20 Gislaved ArcticControl 110T XL',
            id='zapaska-model-from-column-drops-fr',
        ),
        pytest.param(
            {'title': '17.5-25 Rockbuster H108C E3/L3 28PR TT (прерывистая волна)'},
            '17.5-25 Rockbuster H108C E3/L3 28PR TT',
            id='pioner-description-in-brackets-dropped',
        ),
        pytest.param(
            {'title': '285/70R19.5 Triangle TRD02 146/144L 18PR TL ведущая'},
            '285/70R19.5 Triangle TRD02 146/144L 18PR TL Ведущая',
            id='pioner-axis-from-dictionary-truck-keeps-tl',
        ),
        pytest.param(
            {'title': '195/75 R16C Triangle TRIN LL01 8PR 107/105Q'},
            '195/75R16C Triangle TRIN LL01 107/105Q 8PR',
            id='autosnab-space-before-r-and-order',
        ),
        pytest.param(
            {
                'title': '295/80R22.5 Blackhawk (Sailun Group Co., LTD) BDR75 TL M+S 3PMSF 152/149M 18PR',
                'model': 'BDR75',
            },
            '295/80R22.5 Blackhawk BDR75 152/149M 18PR TL M+S 3PMSF',
            id='autosnab-sidewall-marks-kept-owner-dropped',
        ),
        pytest.param(
            {'title': '265/70R16 Sailun Ice Blazer WST3 TL 112T шип'},
            '265/70R16 Sailun Ice Blazer WST3 112T TL',
            id='passenger-tl-kept',
        ),
        pytest.param(
            {'title': '31X10.50R15LT Maxxis Bighorn MT-764 109Q'},
            '31x10.5R15LT Maxxis Bighorn MT-764 109Q',
            id='inch-radial-size',
        ),
        pytest.param(
            {
                'title': '245/35R21 Hankook Ventus S1 evo 3 K127B Run-Flat 96Y XL',
                'model': 'Ventus S1 evo3 K127B',
            },
            '245/35R21 Hankook Ventus S1 evo3 K127B 96Y XL RunFlat',
            id='run-flat-from-title',
        ),
        pytest.param(
            {
                'title': '315/35R20 Maxxis Victra Run-Flat M36+ 110W',
                'model': 'Victra Run-Flat M36+',
            },
            '315/35R20 Maxxis Victra Run-Flat M36+ 110W',
            id='run-flat-already-in-model-not-repeated',
        ),
    ],
)
def test_compose_tire_title(fields: dict[str, str], expected: str) -> None:
    assert _compose(RowItem(fields)) == expected


def test_brand_is_the_manufacturer_found_in_supplier_text() -> None:
    """Бренд — производитель, которого найдёт поиск по алиасам в тексте поставщика, а не колонка с владельцем."""
    row = RowItem({'title': '215/65R16 Cordiant (Bridgestone) Sno-Max 7000 98T', 'manufacturer_name': 'Cordiant'})

    title = TireTitleFromFields(NormalizeTitle(), lambda _title: 'Bridgestone').prepare(row)

    assert title is not None
    assert title.startswith('215/65R16 Bridgestone ')


def test_brand_without_probe_comes_from_manufacturer_field_then_title() -> None:
    with_field = RowItem({'title': '205/55R16 Foo Bar 91V', 'manufacturer_name': 'Baz'})
    without_field = RowItem({'title': '205/55R16 Foo Bar 91V'})

    assert TireTitleFromFields(NormalizeTitle()).prepare(with_field) == '205/55R16 Baz Bar 91V'
    assert TireTitleFromFields(NormalizeTitle()).prepare(without_field) == '205/55R16 Foo Bar 91V'


def test_compose_is_stable_on_second_pass() -> None:
    """Название собирается дважды (обогащение и шаг pipeline): второй проход ничего не меняет."""
    row = RowItem(
        {
            'title': '10.00R20 ИД-304 У-4 18PR 154/149J TT Кама',
            'manufacturer_name': 'Кама',
            'model': 'ИД-304 У-4',
        },
    )

    first = _compose(row)
    row.set_field('title', first)
    second = _compose(row)

    assert first == second == '10.00R20 Кама ИД-304 У-4 154/149J 18PR TT'


def test_fields_win_over_parsed_title() -> None:
    """Заполненные поля главнее разбора названия: слойность, камерность и ось (индексы название и так перебивает)."""
    row = RowItem(
        {
            'title': '11R22.5 Taitong HS103 146/143M 16PR TL',
            'layering': 'PR18',
            'intimacy': 'TT',
            'axis': 'прицепная',
        },
    )

    assert _compose(row) == '11R22.5 Taitong HS103 146/143M 18PR TT Прицепная'


@pytest.mark.parametrize(
    'title',
    ['Автокамера 11.2-20', 'Ободная лента 20.5-25', 'Уплотнительное кольцо 6x70', 'Диск 6.0x15 4x98 ET35'],
)
def test_not_a_tire_is_left_alone(title: str) -> None:
    """Камеры, ленты, кольца и диски не шины: название не меняется, пометки «не собрано» нет."""
    row = RowItem({'title': title})

    assert _compose(row) == title
    assert row.vendor.title_not_composed is None


def test_unparsable_tire_keeps_supplier_text_and_is_marked() -> None:
    """Размер в полях есть, а в названии не разобрался: остаётся текст поставщика, позиция помечена для статистики."""
    row = RowItem({'title': '215/40ZR18 Maxxis Victra Sport VS5 89Y', 'width': '215', 'diameter': '18'})

    assert _compose(row) == '215/40ZR18 Maxxis Victra Sport VS5 89Y'
    assert row.vendor.title_not_composed is True


def test_empty_title_is_passed_through() -> None:
    row = RowItem({})

    assert TireTitleFromFields(NormalizeTitle()).prepare(row) is None
    assert row.vendor.title_not_composed is None


@pytest.mark.parametrize(
    ('count', 'expected'), [(0, ''), (3, 'Название шины не собрано из полей (оставлен текст поставщика), позиций: 3')]
)
def test_titles_not_composed_message(count: int, expected: str) -> None:
    assert titles_not_composed_message(count) == expected


def test_compose_flag_builds_wrapper_that_composes() -> None:
    """Флаг `compose` конфига оборачивает стратегию: она собирает название по полям, разобранным из названия."""
    config = TitleConfig(strategy='normalize_title', params_from_title=True, compose=True)
    row = RowItem({'title': '195/75 R16C Triangle TRIN LL01 8PR 107/105Q', 'manufacturer_name': 'Triangle'})

    strategy = make_title_strategy(config, 'zapaska.json → title')

    assert isinstance(strategy, TireTitleFromFields)
    assert strategy.prepare(row) == '195/75R16C Triangle TRIN LL01 107/105Q 8PR'
