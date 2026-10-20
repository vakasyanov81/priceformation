"""tests for four_tochki title helpers."""

from typing import Any

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies._four_tochki_tire_helper import (
    _fill_size_from_title,
    _tire_kind,
    default_tire_title,
    ext_diameter_title,
    get_prepared_title,
    is_special_tire,
    is_truck_tire,
    truck_title,
)

_SIZE = '205/55R16'
_WRAP = 'XXXX'
_TRUCK = 'грузовая'
_SPECIAL = 'спецтехника'
_EM_DASH = '—'


def test_truck_tire_by_type() -> None:
    assert is_truck_tire(RowItem({'tire_type': 'грузовая'})) is True
    assert is_truck_tire(RowItem({'tire_type': 'ГРУЗОВАЯ'})) is True
    assert is_truck_tire(RowItem({'tire_type': 'легковая'})) is False
    assert is_truck_tire(RowItem({})) is False


def test_special_tire_empty_is_false() -> None:
    assert is_special_tire(RowItem({})) is False
    assert is_special_tire(RowItem({'tire_type': 'спецтехника'})) is True


def test_truck_title_skips_empty_model() -> None:
    assert _WRAP not in truck_title(RowItem({}), _SIZE)


def test_truck_title_keeps_camera_and_sidewall() -> None:
    row = RowItem(
        {
            'manufacturer_name': 'Triangle',
            'model': 'TRD06',
            'layering': '20',
            'camera_type': 'TL',
            'inscription_on_the_side': '3PMSF',
            'index_load': '157/154',
            'index_velocity': 'K',
        }
    )
    title = truck_title(row, '315/80R22.5')
    assert title == '315/80R22.5 Triangle TRD06 157/154K 20PR TL 3PMSF'


def test_default_title_includes_runflat() -> None:
    row = RowItem(
        {
            'manufacturer_name': 'Pirelli',
            'model': 'Scorpion Verde All-Season',
            'camera_type': 'TL',
            'index_load': '103',
            'index_velocity': 'H',
            'run_flat': 'Да',
        }
    )
    title = default_tire_title(row, '235/60R18')
    assert title == '235/60R18 Pirelli Scorpion Verde All-Season 103H TL RunFlat'


def test_ext_diameter_title_skips_empty_optional() -> None:
    row = RowItem({'ext_diameter': 31})
    assert _WRAP not in ext_diameter_title(row, _SIZE)


@pytest.mark.parametrize(
    ('fields', 'expected'),
    [
        ({'width': '205', 'diameter': 'R18'}, '205R18'),
        ({'width': '11', 'diameter': 'R20'}, '11R20'),
        ({'width': '10', 'diameter': 'R18'}, '10R18'),
        ({'width': '11', 'diameter': 'R20', 'tire_type': _TRUCK}, '11.00R20'),
        ({'width': '315', 'diameter': 'R22.5', 'tire_type': _TRUCK}, '315R22.5'),
        ({'width': '11', 'diameter': 'R16', 'tire_type': _TRUCK}, '11R16'),
        (
            {'width': 30.5, 'height_percent': 999.0, 'diameter': '--32'},
            '30.5L-32',
        ),
        (
            {
                'width': 11.0,
                'height_percent': 999.0,
                'diameter': '--15',
                'tire_type': 'спецтехника',
            },
            '11L-15',
        ),
        (
            {
                'width': 12.4,
                'height_percent': 999.0,
                'diameter': '--16',
                'tire_type': 'спецтехника',
            },
            '12.4L-16',
        ),
        ({'width': '11', 'height_percent': 'L.0', 'diameter': '--15'}, '11L-15'),
        (
            {
                'width': 140.0,
                'height_percent': 55.0,
                'diameter': '--9',
                'tire_type': 'спецтехника',
            },
            '140/55-9',
        ),
        # Канонизация десятичной запятой: ширина и диаметр через запятую.
        ({'width': '22,5', 'height_percent': '40', 'diameter': 'R18'}, '22.5/40R18'),
        ({'width': '205', 'height_percent': '55', 'diameter': 'R22,5'}, '205/55R22.5'),
        # RZ в диаметре → ZR в размере.
        ({'width': '205', 'height_percent': '55', 'diameter': 'RZ18'}, '205/55ZR18'),
        # Тире в диаметре → конструкция '-' (не 'R').
        ({'width': '205', 'height_percent': '55', 'diameter': f'{_EM_DASH}32'}, '205/55-32'),
        # Пустой диаметр не подменяется заглушкой.
        ({'width': '205'}, '205R'),
        # Спецшина: суффикс .0 только для дюймового профиля шириной < 100.
        (
            {'width': '15', 'height_percent': '55', 'diameter': 'R15', 'tire_type': _SPECIAL},
            '15.0/55R15',
        ),
        # Та же ширина, но не спецтехника — точка не добавляется.
        ({'width': '15', 'height_percent': '55', 'diameter': 'R15'}, '15/55R15'),
        # Спецшина без профиля — точка не добавляется.
        ({'width': '15', 'diameter': 'R15', 'tire_type': _SPECIAL}, '15R15'),
        # Метрическая ширина 100 — граница, точка не добавляется.
        (
            {'width': '100', 'height_percent': '55', 'diameter': 'R15', 'tire_type': _SPECIAL},
            '100/55R15',
        ),
        # Дробная ширина у спецшины — не digit, точка не добавляется.
        (
            {'width': 30.5, 'height_percent': 55.0, 'diameter': 'R15', 'tire_type': _SPECIAL},
            '30.5/55R15',
        ),
        # Дробная ширина грузовой шины уже содержит доли: `.00` не дописывается (`8.25R20`, не `8.25.00R20`).
        ({'width': '8.25', 'diameter': 'R20', 'tire_type': _TRUCK}, '8.25R20'),
        # Дюймовая пара 10/20 получает суффикс .00.
        ({'width': '10', 'diameter': 'R20'}, '10.00R20'),
    ],
)
def test_prepared_title_width_postfix(fields: dict[str, Any], expected: str) -> None:
    assert get_prepared_title(RowItem(fields)) == expected


def test_default_title_all_parts() -> None:
    """Все поля обычного title попадают в строку целиком."""
    row = RowItem(
        {
            'manufacturer_name': 'Pirelli',
            'model': 'Scorpion',
            'layering': '20',
            'camera_type': 'TL',
            'inscription_on_the_side': '3PMSF',
            'index_load': '103',
            'index_velocity': 'H',
            'run_flat': 'Да',
        }
    )

    assert default_tire_title(row, '235/60R18') == '235/60R18 Pirelli Scorpion 103H 20PR TL 3PMSF RunFlat'


def test_ext_diameter_title_all_parts() -> None:
    """Title с внешним диаметром заполнен всеми необязательными полями."""
    row = RowItem(
        {
            'manufacturer_name': 'Pirelli',
            'model': 'Scorpion',
            'ext_diameter': 31,
            'index_load': '103',
            'us_aff_designation': 'EU',
            'inscription_on_the_side': '3PMSF',
            'run_flat': 'Да',
        }
    )

    assert ext_diameter_title(row, '235/60R18') == '235/60R18 Pirelli Scorpion 103 EU 3PMSF RunFlat'


def _api_tire(title: str, manufacturer: str, model: str, tire_type: str = 'Легковая') -> RowItem:
    """Строка API Форточек: название как пришло из API, колонки бренда, модели и типа."""
    return RowItem({'title': title, 'manufacturer_name': manufacturer, 'model': model, 'tire_type': tire_type})


@pytest.mark.parametrize(
    ('title', 'manufacturer', 'model', 'tire_type', 'expected'),
    [
        # Разбор названия API и сборка по нашим правилам (как у xlsx).
        (
            '205/65R16 95T Brina Nordico V-522 TL (102 шип.)',
            'Viatti',
            'Brina Nordico V-522',
            'Легковая',
            '205/65R16 Viatti Brina Nordico V-522 95T TL',
        ),
        # Диагональ, слойность — числом, камера из названия, надпись на боковине из названия.
        (
            '11,00R20(300R508) 150/146K И-68А TT M+S 16PR + Камера 11,00-20 (300-508) вентиль ГК-145',
            'Kama',
            'И-68А',
            'Грузовая',
            '11.00R20 Kama И-68А 150/146K 16PR TT M+S',
        ),
        (
            '10,0/75-15,3 IMP 12PR 126A6 IM-17 TT РОССИЯ + Камера 10,0/75-15,3 вентиль ЛК (50)',
            'NorTec',
            'IM-17',
            'selhoz',
            '10.0/75-15.3 NorTec IM-17 126A6 12PR TT',
        ),
        (
            '155R13 90/88S Trace (НК-135) TL',
            'Kama',
            'Trace (НК-135)',
            'cartruck',
            '155R13 Kama Trace (НК-135) 90/88S TL',
        ),
        # Суффикс диаметра C у грузовых и легкогрузовых — в диаметре, как в колонке прайса.
        (
            '205/75R16C 110/108R Trace (НК-135) TL',
            'Kama',
            'Trace (НК-135)',
            'cartruck',
            '205/75R16C Kama Trace (НК-135) 110/108R TL',
        ),
        # Конструкции, которых общий разбор не принимает: ZR, префикс P, скорость в скобках.
        (
            '245/45ZR17 99W XL Ingens A1 TL M+S',
            'Antares',
            'Ingens A1',
            'Легковая',
            '245/45ZR17 Antares Ingens A1 99W XL TL M+S',
        ),
        (
            'P225/60R18 104T XL RA1100 TL WW M+S',
            'Roadcruza',
            'RA1100',
            'Легковая',
            '225/60R18 Roadcruza RA1100 104T XL TL M+S',
        ),
        (
            '225/40ZR18 94(Y) XL Pilot Sport 5 TL',
            'Michelin',
            'Pilot Sport 5',
            'Легковая',
            '225/40ZR18 Michelin Pilot Sport 5 94(Y) XL TL',
        ),
        # Камера «только шина» и RunFlat из RFT — как в колонках прайса.
        (
            '425/85R21 Nortec TR-184-1 18PR 156J TT (только шина)',
            'Nortec',
            'TR-184-1',
            'Грузовая',
            '425/85R21 Nortec TR-184-1 156J 18PR TT (только шина)',
        ),
        (
            '235/60R18 103V Scorpion Verde All-Season TL RFT M+S',
            'Pirelli',
            'Scorpion Verde All-Season',
            'Легковая',
            '235/60R18 Pirelli Scorpion Verde All-Season 103V TL M+S RunFlat',
        ),
        # Надпись на боковине стоит после неизвестного слова BSW — она всё равно попадает в название.
        (
            '215/65R16 102V XL Atrezzo 4 Seasons TL BSW M+S 3PMSF',
            'Sailun',
            'Atrezzo 4 Seasons',
            'Легковая',
            '215/65R16 Sailun Atrezzo 4 Seasons 102V XL TL M+S 3PMSF',
        ),
    ],
)
def test_api_title_composed_by_rules(
    title: str,
    manufacturer: str,
    model: str,
    tire_type: str,
    expected: str,
) -> None:
    assert get_prepared_title(_api_tire(title, manufacturer, model, tire_type)) == expected


def test_api_title_composition_is_stable_on_second_pass() -> None:
    """Название собирается дважды (обогащение и шаг pipeline): второй проход не дублирует суффикс."""
    row = _api_tire('155R13C 90/88S Trace (НК-135) TL', 'Kama', 'Trace (НК-135)', 'Легковая')

    first = get_prepared_title(row)
    row.set_field('title', first)
    second = get_prepared_title(row)

    assert first == second == '155R13C Kama Trace (НК-135) 90/88S TL'


def test_unparsable_api_size_keeps_title() -> None:
    """Размер, который не разобрать даже после нормализации, остаётся исходным названием, а не обрезком."""
    title = 'LT35x12,50Z17(320/70R17) 121S RA1100 TL WW M+S'

    assert get_prepared_title(_api_tire(title, 'Roadcruza', 'RA1100')) == title


def test_inch_radial_api_size_is_composed() -> None:
    """Дюймовый радиальный размер `35x12,50R17` разбирается и собирается в канонической записи без лишнего нуля."""
    title = 'LT35x12,50R17(320/70R17) 121S RA1100 TL WW M+S'

    assert get_prepared_title(_api_tire(title, 'Roadcruza', 'RA1100')) == '35x12.5R17 Roadcruza RA1100 121S M+S'


def test_xlsx_columns_path_unchanged_for_special_width() -> None:
    """Колонки прайса без названия собираются прежним правилом: ширина спецшины с .0."""
    row = RowItem({'width': '13.0', 'height_percent': '75.0', 'diameter': '-16', 'tire_type': 'спецтехника'})

    assert get_prepared_title(row) == '13.0/75-16'


def test_fill_size_keeps_existing_width_and_title() -> None:
    """Размер из названия разбирается только при пустой ширине; заполненные поля не трогаются."""
    row = RowItem({'title': 'P225/60R18 100H Brand', 'width': '999'})
    get_prepared_title(row)
    assert row.tire.width == '999'


def test_fill_size_without_title_and_width_is_noop() -> None:
    """Нет ни ширины, ни названия — разбирать нечего, ошибки нет."""
    row = RowItem({})
    _fill_size_from_title(row)
    assert not row.tire.width


def test_fill_size_from_rim_notation_title() -> None:
    """Ободная запись `6,00-9/4,00E` отбрасывается, размер берётся из `6,00-9`."""
    row = RowItem({'title': '6,00-9/4,00E Brand 10PR'})
    get_prepared_title(row)
    assert (row.tire.width, row.tire.diameter) == ('6.00', '9')


def test_prepared_title_strips_trailing_zero_of_fractional_width() -> None:
    """Дробная ширина `7,50` в названии идёт как `7.5`."""
    row = RowItem({'width': '7,50', 'diameter': 'R16', 'manufacturer_name': 'Brand', 'model': 'M'})
    assert get_prepared_title(row).startswith('7.5R16')


def test_suffix_not_added_without_diameter() -> None:
    """Суффикс диаметра дописывается только к существующему диаметру."""
    row = RowItem({'title': '185/75R16C Brand', 'width': '185'})
    get_prepared_title(row)
    assert not row.tire.diameter


def test_tire_kind_without_type_is_empty() -> None:
    """Без типа шины это не грузовая и не спецтехника; пустая строка, а не подстановка."""
    assert _tire_kind(RowItem({})) == ''
    assert _tire_kind(RowItem({'tire_type': 'QuadBike'})) == 'мото'
