"""Разбор и сборка названия номенклатуры Пошка и STK."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies._tire_title_parser import (
    TireTitleParts,
    fill_tire_fields,
    parse_tire_title,
)

# Примеры склейки → Пионер (порядок: размер бренд модель нагрузка/скорость PR камера назначение).
_GLUE_EXAMPLES = (
    (
        '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт',
        '10.00R20 DOUBLEROAD DR-801 149/146K 18PR унив.ось с об/л',
    ),
    (
        '11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, (1 шт)',
        '11R22.5 TAITONG HS103 146/143M 16PR вед.ось',
    ),
    (
        'а/п 425/85R21 NORTEC TR-184-1 18PR 156J TT, шт',
        '425/85R21 NORTEC TR-184-1 156J 18PR TT',
    ),
    (
        '11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт',
        '11.00R20 НКШЗ И-68А 150/146K 16PR',
    ),
    (
        '12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт',
        '12.4L-16 БШК Бел-160М 111A6 8PR сельхозшина',
    ),
    (
        '17.5-25 Rockbuster H108A E3/L3 н.с.28 спецшина, шт',
        '17.5-25 Rockbuster H108A E3/L3 28PR спецшина',
    ),
    # STK
    (
        'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка',
        '11R22.5 GREENSTONE DR668 146/143L 16PR шашка',
    ),
    (
        'Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал',
        '235/75R17.5 LingLong LLA78 143/141J 18PR TL трал',
    ),
    (
        'Автошина 12.00R24 DRC D931 20PR 160/157F TTF карьер',
        '12.00R24 DRC D931 160/157F 20PR TTF карьер',
    ),
    (
        'Автошина 7.00 R16LT14PR 118/114L GREENSTONE ST896 змейка',
        '7.00R16LT GREENSTONE ST896 118/114L 14PR змейка',
    ),
    (
        'Автошина 295/80R22.5 18PR 152/149M GREENSTONE ST33 руль',
        '295/80R22.5 GREENSTONE ST33 152/149M 18PR руль',
    ),
    (
        'Автошина 385/55R22.5 20PR 160K GREENSTONE ST398 руль/прицеп',
        '385/55R22.5 GREENSTONE ST398 160K 20PR руль/прицеп',
    ),
    (
        'Автошина 315/80 R22.5 22PR 167/164D TRANSMATE TMD18 карьер',
        '315/80R22.5 TRANSMATE TMD18 167/164D 22PR карьер',
    ),
    (
        'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка, шт',
        '11R22.5 GREENSTONE DR668 146/143L 16PR шашка',
    ),
    (
        'Автошина 12.00R24 DRC D931 20PR 160/157F TTF карьер, , шт',
        '12.00R24 DRC D931 160/157F 20PR TTF карьер',
    ),
    (
        'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка, (12 шт)',
        '11R22.5 GREENSTONE DR668 146/143L 16PR шашка',
    ),
    (
        'Автопокрышка 12.00R24 DRC D931 20PR 160/157F TTF карьер',
        '12.00R24 DRC D931 160/157F 20PR TTF карьер',
    ),
    (
        'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка автопокрышка',
        '11R22.5 GREENSTONE DR668 146/143L 16PR шашка',
    ),
    (
        'Автошина 11.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л',
        '11.00R20 DOUBLEROAD DR-801 149/146K 18PR унив.ось с об/л',
    ),
)


@pytest.mark.parametrize(('raw', 'expected'), _GLUE_EXAMPLES)
def test_parse_and_compose_examples(raw: str, expected: str) -> None:
    """Склейка примера даёт порядок Пионера."""
    parts = parse_tire_title(raw)

    assert parts is not None
    assert parts.compose() == expected


@pytest.mark.parametrize(('raw', 'expected'), _GLUE_EXAMPLES)
def test_compose_uses_brand_over_parsed(raw: str, expected: str) -> None:
    """Канонический бренд из поля перекрывает разобранный токен."""
    parts = parse_tire_title(raw)

    assert parts is not None
    assert parts.compose('Brand') == expected.replace(parts.brand, 'Brand', 1)


def test_parse_splits_size_and_parameters() -> None:
    """Размер и параметры разобраны по отдельным полям."""
    parts = parse_tire_title('10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт')

    assert parts is not None
    assert parts.size.label == '10.00R20'
    assert parts.size.width == '10.00'
    assert parts.size.height_percent == ''
    assert parts.size.diameter == '20'
    assert (parts.brand, parts.model) == ('DOUBLEROAD', 'DR-801')
    assert (parts.load, parts.velocity) == ('149/146', 'K')
    assert (parts.layering, parts.intimacy) == ('18PR', '')
    assert parts.usage == ('унив.ось', 'с', 'об/л')


def test_parse_makes_producer_the_brand() -> None:
    """Производитель из хвоста становится брендом, если бренда в начале нет."""
    parts = parse_tire_title('11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт')

    assert parts is not None
    assert parts.brand == 'НКШЗ'
    assert parts.model == 'И-68А'
    assert parts.usage == ()


def test_parse_joins_split_size_and_low_marker() -> None:
    """Маркер низкого профиля ``L`` сохраняется, ``, шт`` срезается."""
    parts = parse_tire_title('12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт')

    assert parts is not None
    assert parts.size.label == '12.4L-16'
    assert parts.size.width == '12.4'
    assert parts.brand == 'БШК'
    assert parts.model == 'Бел-160М'
    assert parts.layering == '8PR'
    assert parts.load == '111'
    assert parts.velocity == 'A6'


def test_parse_brand_keeps_producer_in_tail() -> None:
    """Латинский бренд/«Кама» в начале перекрывает производителя, тот едет в хвост."""
    tyrex = parse_tire_title('11.00 R20 Tyrex CRG VM-310 н.с.16 150/146K ОШЗ автошина, (1 шт)')
    kama = parse_tire_title('10.00 R20 КАМА-310 146/143K 16PR НКШЗ автошина, шт')

    assert tyrex is not None
    assert (tyrex.brand, tyrex.model) == ('Tyrex', 'CRG VM-310')
    assert tyrex.usage == ('ОШЗ',)
    assert kama is not None
    assert (kama.brand, kama.model) == ('КАМА-310', '')
    assert kama.usage == ('НКШЗ',)


def test_parse_joins_split_pr_and_strips_kind_suffix() -> None:
    """Разорванный ``8 PR`` склеивается, суффикс ``*автопокрышка`` срезается."""
    split_pr = parse_tire_title('185/75 R16C THREE-A TRACVAN IMP 104/102R 8 PR б/к автопокрышка, шт')
    suffix = parse_tire_title('185/75 R16С Sonix Winter X Pro Studs 77 104/102R шип.автопокрышка, шт')

    assert split_pr is not None
    assert split_pr.layering == '8PR'
    assert split_pr.usage == ('б/к',)
    assert suffix is not None
    assert suffix.usage == ('шип.',)


def test_parse_returns_none_for_disk() -> None:
    """Диск — не размер шины: разбор не срабатывает."""
    assert parse_tire_title('Диск штамп NORTEC-16 11.75*22.5 10*335 ET0 d281 , шт') is None


_NONSTANDARD = (
    ('500/70-508(1200х500-508) Forward Traction 500 TT', '500/70-508', '(1200x500-508)', 'Forward', 'Traction 500'),
    ('265/80-16(33х10.5-16) Nortec AT-100 TL', '265/80-16', '(33x10.5-16)', 'Nortec', 'AT-100'),
    ('18x7-8 (180/70-8) Haulking HK-100 TT', '18x7-8', '(180/70-8)', 'Haulking', 'HK-100'),
    ('8.15-15 (28х9-15) Rockbuster H107 14PR TT', '8.15-15', '(28x9-15)', 'Rockbuster', 'H107'),
    ('16/70-20 (405/70-20) Rockbuster H100 TT', '16/70-20', '(405/70-20)', 'Rockbuster', 'H100'),
    ('165-13/6.45-13 Forward М-145 78P TT', '165-13', '/6.45-13', 'Forward', 'М-145'),
)


@pytest.mark.parametrize(('raw', 'label', 'alt', 'brand', 'model'), _NONSTANDARD)
def test_parse_alternative_size_does_not_cut_tail(raw: str, label: str, alt: str, brand: str, model: str) -> None:
    """Размер в скобках или через ``/`` — альтернативная запись: разбор идёт дальше и не теряет её."""
    parts = _parsed(raw)

    assert (parts.size.label, parts.size.alt) == (label, alt)
    assert (parts.brand, parts.model) == (brand, model)
    glue = '' if alt.startswith('/') else ' '
    assert parts.compose().startswith(f'{label}{glue}{alt} {brand}')


@pytest.mark.parametrize(
    ('raw', 'label', 'ext', 'width', 'diameter'),
    [
        ('33х12.5-15 Forward Safari-500 108L TL', '33x12.5-15', '33', '12.5', '15'),
        ('31х10.5-15LT Forward Safari 500 TL', '31x10.5-15LT', '31', '10.5', '15'),
        ('1220х400-533 Forward Traction 500', '1220x400-533', '1220', '400', '533'),
        ('16*6-8 Rockbuster H100 TT', '16x6-8', '16', '6', '8'),
        ('18x7-8 Haulking HK-100 TT', '18x7-8', '18', '7', '8'),
    ],
)
def test_parse_inch_size_has_ext_diameter(raw: str, label: str, ext: str, width: str, diameter: str) -> None:
    """Размер «внешний x ширина - посадочный»: внешний диаметр отдельным полем."""
    size = _parsed(raw).size

    assert (size.label, size.ext_diameter) == (label, ext)
    assert (size.width, size.diameter) == (width, diameter)
    assert size.height_percent == ''


def test_parse_finds_size_inside_title() -> None:
    """Размер не в начале: слова до него уходят в бренд/модель, слова после — в назначение."""
    parts = _parsed('Forward Professional 153 а/ш 225/75R16 кам зимняя шип')

    assert parts.size.label == '225/75R16'
    assert (parts.brand, parts.model) == ('Forward', 'Professional 153')
    assert parts.usage == ('кам', 'зимняя', 'шип')


def test_parse_ignores_inner_size_after_other_size() -> None:
    """Если до радиального размера уже стоит другой размер, основным он не считается."""
    assert parse_tire_title('Forward 12x5-8 TT 225/75R16') is None


def test_fill_tire_fields_sets_ext_diameter() -> None:
    raw = '33х12.5-15 Forward Safari-500 108L TL'
    row = RowItem({'title': raw})

    fill_tire_fields(row, _parsed(raw))

    assert row.tire.ext_diameter == 33
    assert row.tire.width == '12.5'


def test_parse_returns_none_without_brand_model() -> None:
    """Только размер и служебные токены — модели нет, разбор пуст."""
    assert parse_tire_title('Автошина 11R22.5 16PR 146/143L') is None


def test_parse_returns_none_for_producer_without_model() -> None:
    """Один производитель без бренда с моделью — разбор пуст."""
    assert parse_tire_title('Автошина 12.00R20 16PR 150/146K НКШЗ') is None


def test_fill_tire_fields_sets_parameters() -> None:
    """Разобранные параметры попадают в поля позиции."""
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт'})
    parts = parse_tire_title(row.identity.title)

    assert parts is not None
    fill_tire_fields(row, parts)

    assert row.tire.width == '10.00'
    assert row.tire.height_percent is None
    assert row.tire.diameter == '20'
    assert row.tire.layering == '18PR'
    assert row.tire.index_load == '149/146'
    assert row.tire.index_velocity == 'K'
    assert row.identity.model == 'DR-801'


def test_fill_tire_fields_keeps_existing_values() -> None:
    """Уже заполненные поля разбор не перетирает."""
    row = RowItem(
        {
            'title': '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт',
            'width': '999',
            'model': 'Old',
        },
    )
    parts = parse_tire_title(row.identity.title)

    assert parts is not None
    fill_tire_fields(row, parts)

    assert row.tire.width == '999'
    assert row.identity.model == 'Old'


def test_fill_tire_fields_title_overrides_load_and_speed_index() -> None:
    """Индекс нагрузки/скорости из названия главнее колонки: колонка Запаски дана по модели, а не по артикулу."""
    row = RowItem(
        {
            'title': '185/65R14 Hankook Kinergy Eco 2 K435 86T',
            'index_load': '82',
            'index_velocity': 'H',
        },
    )
    parts = parse_tire_title(row.identity.title)

    assert parts is not None
    fill_tire_fields(row, parts)

    assert row.tire.index_load == '86'
    assert row.tire.index_velocity == 'T'


def test_fill_tire_fields_keeps_column_index_when_title_has_none() -> None:
    """Нет индекса в названии — колонка остаётся."""
    row = RowItem({'title': '185/65R14 Hankook Kinergy Eco 2 K435', 'index_load': '86', 'index_velocity': 'H'})
    parts = parse_tire_title(row.identity.title)

    if parts is not None:
        fill_tire_fields(row, parts)

    assert row.tire.index_load == '86'
    assert row.tire.index_velocity == 'H'


_SPIKE_CASES = (
    ('', 'Да'),
    (None, 'Да'),
    ('Нет', 'Да'),
    ('да', 'да'),
    ('Да', 'Да'),
)


@pytest.mark.parametrize(('column', 'expected'), _SPIKE_CASES)
def test_fill_tire_fields_spike_in_title_wins(column: str | None, expected: str) -> None:
    """«шип» в названии главнее колонки «Нет»; готовое `да` другого регистра не переписывается."""
    raw = '235/45R17 Kumho WinterCraft Ice WI32 97T XL шип'
    row = RowItem({'title': raw, 'spike': column})

    fill_tire_fields(row, _parsed(raw))

    assert row.tire.spike == expected


def test_fill_tire_fields_no_spike_in_title_keeps_column() -> None:
    """Нет «шип» в названии — колонка остаётся: название без шипа не опровергает шипованную шину."""
    raw = '265/40R22 Sailun Ice Blazer WST3 106T'
    row = RowItem({'title': raw, 'spike': 'Да'})

    fill_tire_fields(row, _parsed(raw))

    assert row.tire.spike == 'Да'


_FILLED_FIELDS = (
    'width',
    'height_percent',
    'diameter',
    'layering',
    'index_load',
    'index_velocity',
    'intimacy',
    'model',
)


def _parsed(raw: str) -> TireTitleParts:
    parts = parse_tire_title(raw)
    assert parts is not None
    return parts


def _filled(row: RowItem) -> dict[str, object]:
    return {key: row.get_field(key) for key in _FILLED_FIELDS}


def test_fill_tire_fields_sets_every_field() -> None:
    """Все разобранные параметры, включая профиль и камерность, попадают в свои поля."""
    row = RowItem({'title': 'Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал'})

    fill_tire_fields(row, _parsed('Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал'))

    assert _filled(row) == {
        'width': '235',
        'height_percent': '75',
        'diameter': '17.5',
        'layering': '18PR',
        'index_load': '143/141',
        'index_velocity': 'J',
        'intimacy': 'TL',
        'model': 'LLA78',
    }


@pytest.mark.parametrize('raw', [None, ''], ids=['none', 'empty'])
def test_parse_empty_title(raw: str | None) -> None:
    """Пустое название не разбирается."""
    assert parse_tire_title(raw) is None


@pytest.mark.parametrize(
    ('raw', 'label', 'width', 'height', 'diameter'),
    [
        ('7,00 R16 GREENSTONE ST896', '7.00R16', '7.00', '', '16'),
        ('11 R22,5 TAITONG HS103', '11R22.5', '11', '', '22.5'),
        ('185/75 r16c Sonix Ice', '185/75R16C', '185', '75', '16'),
        ('205/70r15lt Sonix Ice', '205/70R15LT', '205', '70', '15'),
        ('12.4L-16 Бел-160М', '12.4L-16', '12.4', '', '16'),
        ('12.4l-16 Бел-160М', '12.4L-16', '12.4', '', '16'),
    ],
    ids=['comma-width', 'comma-diameter', 'lower-r-suffix-c', 'lower-lt', 'low-profile', 'low-profile-lower'],
)
def test_parse_size_parts(raw: str, label: str, width: str, height: str, diameter: str) -> None:
    """Размер: десятичная запятая → точка, конструкция и суффикс в верхнем регистре."""
    size = _parsed(raw).size

    parsed = (size.label, size.width, size.height_percent, size.diameter)
    assert parsed == (label, width, height, diameter)


def test_parse_strips_commas_only_at_token_edges() -> None:
    """С токенов снимаются только запятые: бренд с запятой и модель на «X» не портятся."""
    parts = _parsed('11R22.5 GREENSTONE, ROADX 16PR')

    assert (parts.brand, parts.model) == ('GREENSTONE', 'ROADX')


@pytest.mark.parametrize(
    'raw',
    ['10.00 R20 (Китай) DOUBLEROAD DR-801', '10.00 R20 /11.00 R20 DOUBLEROAD DR-801'],
    ids=['paren', 'slash'],
)
def test_parse_rejects_bracket_or_slash_after_size(raw: str) -> None:
    """Скобка или слэш сразу после размера (через пробелы) — это не название шины."""
    assert parse_tire_title(raw) is None


def test_parse_brand_starting_with_x() -> None:
    """Бренд на «X» сразу после размера разбирается как обычный."""
    parts = _parsed('11R22.5 XCEED XR1 16PR')

    assert (parts.brand, parts.model, parts.layering) == ('XCEED', 'XR1', '16PR')


@pytest.mark.parametrize(
    ('raw', 'layering'),
    [
        ('11R22.5 GREENSTONE DR668 16 PR', '16PR'),
        ('11R22.5 GREENSTONE DR668 16 pr, шт', '16PR'),
        ('11R22.5 GREENSTONE DR668 н.с.16', '16PR'),
        ('11R22.5 GREENSTONE DR668 16pr', '16PR'),
    ],
    ids=['split', 'split-lower-comma', 'layer-source', 'lower'],
)
def test_parse_layering_forms(raw: str, layering: str) -> None:
    """Слойность в любой записи приводится к ``NPR`` и не попадает в модель."""
    parts = _parsed(raw)

    assert (parts.model, parts.layering) == ('DR668', layering)


def test_parse_keeps_digit_before_non_pr_word() -> None:
    """Число перед обычным словом не склеивается в ``PR``."""
    parts = _parsed('11R22.5 GREENSTONE DR 668 PRO')

    assert (parts.model, parts.layering) == ('DR 668 PRO', '')


@pytest.mark.parametrize(
    ('raw', 'from_ship'),
    [('Шина 11.00R20 И-111А 16PR', True), ('11.00R20 И-111А 16PR НКШЗ', False)],
    ids=['ship', 'plain'],
)
def test_parse_marks_leading_ship(raw: str, from_ship: bool) -> None:
    """Ведущая обёртка «Шина» запоминается для бренда-заглушки."""
    assert _parsed(raw).from_ship is from_ship


@pytest.mark.parametrize(
    ('raw', 'brand', 'expected'),
    [
        ('11R22.5 GREENSTONE DR668 16PR', 'GreenStone', '11R22.5 GreenStone DR668 16PR'),
        ('6L-12 Алтайшина-421 2PR 44A6 TT', 'Алтайшина', '6L-12 Алтайшина-421 44A6 2PR TT'),
        ('10.00 R20 КАМА-310 146/143K 16PR НКШЗ', 'Кама', '10.00R20 Кама-310 146/143K 16PR НКШЗ'),
        ('11R22.5 DOUBLE ROAD DR-801 16PR', 'Double Road', '11R22.5 Double Road ROAD DR-801 16PR'),
        ('11R22.5 GREENSTONE DR668 16PR', None, '11R22.5 GREENSTONE DR668 16PR'),
    ],
    ids=['respell', 'glued-model', 'glued-model-kama', 'other-spelling', 'no-canonical'],
)
def test_compose_canonical_brand_keeps_glued_model(raw: str, brand: str | None, expected: str) -> None:
    """Канонический бренд заменяет только начало токена: слитная модель не теряется."""
    assert _parsed(raw).compose(brand) == expected


@pytest.mark.parametrize(
    ('raw', 'label', 'brand'),
    [
        ('205/55R16 Cordiant Sport 3 94V', '205/55R16', 'Cordiant'),
        ('11R22.5 Continental HDR 148/145L', '11R22.5', 'Continental'),
        ('185/75R16C Cordiant Business 104/102R', '185/75R16C', 'Cordiant'),
        ('7.00 R16LT14PR GREENSTONE ST896', '7.00R16LT', 'GREENSTONE'),
        ('185/75R16С Кама НК-243', '185/75R16С', 'Кама'),
    ],
    ids=['brand-c', 'brand-c-truck', 'suffix-c', 'suffix-lt-glued-pr', 'suffix-cyrillic'],
)
def test_suffix_does_not_bite_brand(raw: str, label: str, brand: str) -> None:
    """Суффикс C/LT отделён от бренда: первая буква `Cordiant` не уходит в размер."""
    parts = _parsed(raw)

    assert (parts.size.label, parts.brand) == (label, brand)


def test_parse_rejects_bracket_after_suffix() -> None:
    """Скобка после суффикса и пробела — тоже не название шины."""
    assert parse_tire_title('185/75R16C (Китай) Cordiant Business') is None


@pytest.mark.parametrize(
    ('raw', 'construction'),
    [
        ('215/75R17.5 Triangle TR685 135/133L 16PR TL рулевая', 'радиальная'),
        ('12.4L-16 БШК Бел-160М 111A6 8PR сельхозшина', 'диагональная'),
        ('165-13/6.45-13 Forward М-145 78P TT', 'диагональная'),
        ('33х12.5-15 Forward Safari-500 108L TL', 'диагональная'),
    ],
)
def test_fill_sets_construction_type(raw: str, construction: str) -> None:
    """`R` в размере — радиальная, дефис и дюймовая запись — диагональная."""
    row = RowItem({'title': raw})
    parts = parse_tire_title(raw)

    assert parts is not None
    fill_tire_fields(row, parts)

    assert row.tire.construction_type == construction


@pytest.mark.parametrize(
    ('raw', 'axis'),
    [
        ('215/75R17.5 Triangle TR685 135/133L 16PR TL рулевая', 'рулевая'),
        ('10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л', 'универсальная'),
        ('11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось', 'ведущая'),
        ('385/65R22.5 Triangle TR656 160K 20PR TL приц.', 'прицепная'),
        ('385/65R22.5 Triangle TR656 160K 20PR TL рулевая/трал', 'рулевая'),
        ('385/65R22.5 Triangle TR656 160K 20PR TL', ''),
    ],
)
def test_fill_sets_axis(raw: str, axis: str) -> None:
    """Ось — из слова назначения; без слова поле пусто."""
    row = RowItem({'title': raw})
    parts = parse_tire_title(raw)

    assert parts is not None
    fill_tire_fields(row, parts)

    assert (row.tire.axis or '') == axis


@pytest.mark.parametrize(
    ('raw', 'model'),
    [
        ('10.00R20 ОИ-73Б 146/143K 16PR TT', 'ОИ-73Б'),
        ('9.00R20 И-Н142Б 140/137K 14PR TT', 'И-Н142Б'),
        ('175/80R16 ВЛИ-10 88Q TT', 'ВЛИ-10'),
        ('185/75R16C БС-1 104/102Q TL', 'БС-1'),
        ('13.6-38 Я-166 129A6 6PR TT', 'Я-166'),
        ('15.5/65-18 КФ-105А 137A6 10PR TL', 'КФ-105А'),
    ],
)
def test_factory_code_is_model_not_brand(raw: str, model: str) -> None:
    """Заводской код без бренда — модель; бренд пуст, а не равен коду."""
    parts = parse_tire_title(raw)

    assert parts is not None
    assert (parts.brand, parts.model) == ('', model)


@pytest.mark.parametrize(
    ('raw', 'brand', 'model'),
    [
        ('425/85R21 ALT A-260 173E 22PR TT', 'ALT', 'A-260'),
        ('225/75R16C Кама-218 121N НКШЗ', 'Кама-218', ''),
        ('175/70R13 КАМА-310 82T', 'КАМА-310', ''),
    ],
)
def test_brand_with_digits_stays_brand(raw: str, brand: str, model: str) -> None:
    """Бренд (латиница, `Кама-218`, `КАМА-310`) под правило заводского кода не попадает."""
    parts = parse_tire_title(raw)

    assert parts is not None
    assert (parts.brand, parts.model) == (brand, model)


@pytest.mark.parametrize(
    ('raw', 'model'),
    [
        ('10.00R20 Кама-310 146/143K 16PR НКШЗ', 'Кама-310'),
        ('8.25R20 Алтайшина-111 125/122J 10PR TT', 'Алтайшина-111'),
        ('6L-12 Алтайшина-421 44A6 2PR TT', 'Алтайшина-421'),
        ('185/75R16 Кама FLAME A/T (HK-245) 97T НКШЗ', 'FLAME A/T (HK-245)'),
        ('175/70R13 Rapid 82T', ''),
    ],
)
def test_fill_sets_model_for_brand_with_glued_model(raw: str, model: str) -> None:
    """Бренд со слитной моделью даёт модель целиком; обычный бренд без модели модель не получает."""
    row = RowItem({'title': raw})
    parts = parse_tire_title(raw)

    assert parts is not None
    fill_tire_fields(row, parts)

    assert (row.identity.model or '') == model
