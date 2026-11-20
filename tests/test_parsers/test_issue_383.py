"""Регрессии определения сезонности и типа шин из задачи #383."""

import pytest

from domain.exceptions import ConfigValidationError
from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.base_parser_title import replace_season
from parsers.base_parser.category_service import CategoryLookup, CategoryService
from parsers.base_parser.config_driven_parser import strategy_hooks_from_section
from parsers.base_parser.parse_statistic import ParserStats
from parsers.strategies.product_type import ProductTypeClassifier
from parsers.strategies.tire_category import TireSizeCategory
from parsers.vendor_config.provider import load_vendor_configs
from parsers.vendor_config.slot_configs import ModelSeasonRules, TitleConfig

_ALL_SEASON = 'Всесезонная'
_WINTER = 'Зимняя'
_SUMMER = 'Летняя'
_SPECIAL = 'Спецшина'


@pytest.fixture
def model_seasons(example_vendors_provider: FakeConfigProvider) -> ModelSeasonRules:
    config = load_vendor_configs(example_vendors_provider)['zapaska']
    section = config.sections[0]
    return strategy_hooks_from_section(section, section.behavior, example_vendors_provider).model_seasons


@pytest.mark.parametrize(
    ('title', 'season'),
    [
        ('7.00R16LT GreenStone ST896 118/114L 14PR', _ALL_SEASON),
        ('185/75R16C Triangle TR646 104/102Q 8PR TL', _ALL_SEASON),
        ('7.00R16LT Triangle TR558 118/114L 14PR TT Рулевая', _ALL_SEASON),
        ('7.00R16LT Triangle TR668A 118/114L 14PR TT Универсальная', _ALL_SEASON),
        ('7.50R16LT Triangle TR668 122/118L 14PR TT Универсальная', _ALL_SEASON),
        ('7.00R16LT Triangle TRD99 118/114K 14PR TT Ведущая', _WINTER),
        ('225/75R16C Triangle SnowLink Trin LL01 121/120R 10PR TL M+S 3PMSF', _WINTER),
        ('215/75R16C Triangle TRIN 113/111Q 8PR LL01', _WINTER),
        ('21x8-9 Rockbuster H989 14PR TT', _ALL_SEASON),
        ('8.15-15 (28x9-15) Rockbuster H989 16PR TT', _ALL_SEASON),
        ('195/75R16C Triangle TR652 107/105R 8PR TL', _SUMMER),
        ('195/75R16C Triangle TV701 110/108T 10PR TL', _SUMMER),
        ('225/75R16C Triangle TV701 121/120S 12PR TL', _SUMMER),
        ('235/65R16C Triangle TV701 115/113S 8PR TL', _SUMMER),
        ('Triangle ConneX Van TV701', _SUMMER),
        ('Triangle SnowLink Trin PL02', _WINTER),
        ('Triangle TR680', _ALL_SEASON),
        ('185/75R16C ДругойБренд TR646', None),
        ('Triangle TV7010', None),
    ],
)
def test_missing_season_by_model(title: str, season: str | None, model_seasons: ModelSeasonRules) -> None:
    assert replace_season(RowItem({'title': title}), model_seasons) == season


@pytest.mark.parametrize(('supplier_season', 'expected'), [(None, _ALL_SEASON), ('лето', _SUMMER)])
def test_model_season_from_source_title(
    supplier_season: str | None,
    expected: str,
    model_seasons: ModelSeasonRules,
) -> None:
    row = RowItem(
        {
            'title': '185/75R16 Triangle 104/102Q',
            'source_title': '185/75R16 Triangle TR646 104/102Q',
            'season': supplier_season,
        },
    )
    assert replace_season(row, model_seasons) == expected


def test_invalid_model_season_pattern_has_config_path() -> None:
    with pytest.raises(ConfigValidationError, match=r'demo\.json → title → model_seasons'):
        TitleConfig.from_dict({'model_seasons': {'(': _WINTER}}, 'demo.json → title')


def test_invalid_model_season_has_config_path() -> None:
    with pytest.raises(ConfigValidationError, match=r'demo\.json → title → model_seasons → triangle tv701'):
        TitleConfig.from_dict({'model_seasons': {'triangle tv701': 'Летнняя'}}, 'demo.json → title')


@pytest.mark.parametrize('size', ['21x8-9', '8.15-15 (28x9-15)'])
def test_rockbuster_h989_is_industrial(size: str) -> None:
    row = RowItem({'title': f'{size} Rockbuster H989 14PR TT'})
    assert ProductTypeClassifier().classify(row) == _SPECIAL
    assert TireSizeCategory().resolve(row) == _SPECIAL


@pytest.mark.parametrize(
    ('category', 'season'),
    [
        ('Грузовая', _ALL_SEASON),
        ('Грузовые', _ALL_SEASON),
        ('Спецшины', _ALL_SEASON),
        ('Сельхоз', _ALL_SEASON),
        ('Индустриальная', _ALL_SEASON),
        ('Легковая', 'Летняя'),
    ],
)
def test_zapaska_season_by_declared_type(
    example_vendors_provider: FakeConfigProvider,
    category: str,
    season: str,
) -> None:
    config = load_vendor_configs(example_vendors_provider)['zapaska']
    section = next(section for section in config.sections if section.id == '22')
    hooks = strategy_hooks_from_section(section, section.behavior, example_vendors_provider)
    categories = CategoryService(hooks, CategoryLookup(ParserStats()))
    row = RowItem({'type_production': category, 'season': 'Летняя'})

    categories.apply_category(row)
    categories.apply_category_fields(row)

    assert row.tire.season == season
