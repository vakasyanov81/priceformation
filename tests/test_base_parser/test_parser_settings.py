"""ParserSettings: конфиг, имя поставщика, признак активности — без BaseParser."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfigNotSetError,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.parser_settings import ParserSettings

_SUPPLIER_NAME = 'Поставщик'
_SHEET = 'лист 2'


def _config(sheet_info: str = '') -> ParseConfiguration:
    price_params = ParserParams(
        supplier=ParseParamsSupplier(folder_name='x', name=_SUPPLIER_NAME, code='x'),
        start_row=1,
        sheet_info=sheet_info,
        columns={},
        stop_words=(),
        file_templates=(),
        sheet_indexes=(0,),
        row_item_adaptor=RowItem,
    )
    aliases_provider = MagicMock()
    aliases_provider.get_aliases.return_value = {}
    return ParseConfiguration(
        BasePriceParseConfigurationParams(
            markup_rules_provider=MagicMock(),
            black_list_provider=MagicMock(),
            manufacturer_aliases=aliases_provider,
            parser_params=price_params,
        )
    )


def test_parse_config_raises_without_config() -> None:
    with pytest.raises(ParseConfigNotSetError):
        ParserSettings().parse_config()


def test_title_is_supplier_name() -> None:
    assert ParserSettings(_config()).title() == _SUPPLIER_NAME


def test_title_adds_sheet_info() -> None:
    assert ParserSettings(_config(_SHEET)).title() == f'{_SUPPLIER_NAME} ({_SHEET})'


def test_manufacturer_finder_is_cached_until_config_changes() -> None:
    settings = ParserSettings(_config())
    first = settings.manufacturer_finder()
    assert settings.manufacturer_finder() is first

    settings.set_parse_config(_config())

    assert settings.manufacturer_finder() is not first


def test_is_active_without_vendor_config() -> None:
    """Легаси-вендор без `_vendor_config` считается включённым."""
    assert ParserSettings(_config()).is_active is True


@pytest.mark.parametrize('enabled', [True, False])
def test_is_active_follows_vendor_config(enabled: bool) -> None:
    config = _config()
    config._vendor_config = SimpleNamespace(enabled=enabled)  # noqa: WPS437

    assert ParserSettings(config).is_active is enabled
