"""tests for the vendor registry module

NOTE: _registry is a global module-level dict that may be pre-populated
with real vendors (from vendor module imports) in the same process.
Tests that touch it must restore the previous state (see the
clear_registry and populates_when_empty tests). Use unique vendor codes
and check specific entries.
"""

from unittest.mock import MagicMock, patch

from parsers.registry import (
    _registry,
    all_vendors_from_registry,
    clear_registry,
    register_vendor,
    vendor_markup_policy_for,
)

# fmt: off
# fmt: on

# NOTE: _FakeBaseParser is a minimal stand-in for BaseParser for testing.
# Type errors below are expected because _FakeBaseParser does not inherit from BaseParser.
# This is acceptable for test code (AGENTS.md: "Tests: fixture literals, float asserts, stubs.")


class _FakeBaseParser:
    """Minimal stand-in for BaseParser to test registry."""

    _vendor_code: str = ''
    _markup_policy_type = None
    _enabled_by_default = True

    @classmethod
    def supplier_folder_name(cls) -> str:
        return 'fake_vendor'

    @classmethod
    def parser_params(cls):  # type: ignore[no-untyped-def]
        from parsers.base_parser.base_parser_config import (
            ParseParamsSupplier,
            ParserParams,
        )
        from parsers.row_item.row_item import RowItem

        return ParserParams(
            supplier=ParseParamsSupplier(
                folder_name='fake_vendor',
                name='Fake Vendor',
                code='99',
            ),
            start_row=0,
            sheet_info='',
            columns={0: RowItem.code.name, 1: RowItem.title.name},
            stop_words=[],
            file_templates=['fake*.xls'],
            sheet_indexes=[],
            row_item_adaptor=RowItem,
        )


# All tests use unique vendor codes to avoid conflicts with real vendors
# and with each other in xdist workers.


_UNIQUE = '_test_unique_vendor_for_registry_test'


def test_register_vendor_sets_attributes() -> None:
    """Декоратор устанавливает _vendor_code, _markup_policy_type, _enabled_by_default."""

    @register_vendor(_UNIQUE + '_1', markup_policy='map_on_opt', enabled_by_default=False)
    class TestParser(_FakeBaseParser):  # noqa: WPS431
        pass

    assert TestParser._vendor_code == _UNIQUE + '_1'  # noqa: WPS336
    assert TestParser._markup_policy_type == 'map_on_opt'  # noqa: WPS336
    assert TestParser._enabled_by_default is False  # type: ignore[unreachable]


def test_register_vendor_defaults() -> None:
    """По умолчанию enabled_by_default=True, markup_policy=None."""

    @register_vendor(_UNIQUE + '_2')
    class DefaultParser(_FakeBaseParser):  # noqa: WPS431
        pass

    assert DefaultParser._vendor_code == _UNIQUE + '_2'
    assert DefaultParser._markup_policy_type is None
    assert DefaultParser._enabled_by_default is True


def test_registry_contains_registered_vendor() -> None:
    """После регистрации класс есть в _registry."""
    code = _UNIQUE + '_3'

    @register_vendor(code)
    class RegParser(_FakeBaseParser):  # noqa: WPS431
        pass

    assert code in _registry
    assert _registry[code] is RegParser


def test_registry_is_global_dict() -> None:
    """_registry — один глобальный dict, пополняется декоратором."""
    code_a = _UNIQUE + '_4a'
    code_b = _UNIQUE + '_4b'

    @register_vendor(code_a)
    class FirstParser(_FakeBaseParser):  # noqa: WPS431
        pass

    @register_vendor(code_b)
    class SecondParser(_FakeBaseParser):  # noqa: WPS431
        pass

    assert code_a in _registry
    assert code_b in _registry


def test_all_vendors_from_registry_returns_list_of_tuples() -> None:
    """all_vendors_from_registry() возвращает список (класс, config)."""
    code_a = _UNIQUE + '_5a'
    code_b = _UNIQUE + '_5b'

    @register_vendor(code_a)
    class VendorA(_FakeBaseParser):  # noqa: WPS431
        pass

    @register_vendor(code_b)
    class VendorB(_FakeBaseParser):  # noqa: WPS431
        pass

    vendors = all_vendors_from_registry()
    assert isinstance(vendors, list)
    assert len(vendors) >= 2  # may also contain real vendors
    classes = {vendor[0] for vendor in vendors}
    assert VendorA in classes
    assert VendorB in classes
    for _cls, config in vendors:
        assert isinstance(config, object)  # ParseConfiguration


def test_config_falls_back_when_make_config_invalid() -> None:
    """make_config вернул не ParseConfiguration — fallback на parser_params."""

    @register_vendor(_UNIQUE + '_5c')
    class BadMakeConfigParser(_FakeBaseParser):  # noqa: WPS431
        @classmethod
        def make_config(cls) -> str:
            return 'not a config'

    config = {parser: cfg for parser, cfg in all_vendors_from_registry()}[BadMakeConfigParser]
    assert config.supplier.folder_name == 'fake_vendor'


def test_vendor_markup_policy_for_returns_none_when_no_policy() -> None:
    """Если у vendor_cls нет _markup_policy_type, возвращаем None."""

    @register_vendor(_UNIQUE + '_6')
    class NoPolicy(_FakeBaseParser):  # noqa: WPS431
        pass

    policy = vendor_markup_policy_for(NoPolicy, MagicMock())
    assert policy is None


def test_vendor_markup_policy_for_identity() -> None:
    """identity → IdentityMarkupPolicy.create()."""
    from parsers.base_parser.markup_policy import IdentityMarkupPolicy

    @register_vendor(_UNIQUE + '_7', markup_policy='identity')
    class IdentityVendor(_FakeBaseParser):  # noqa: WPS431
        pass

    policy = vendor_markup_policy_for(IdentityVendor, MagicMock())
    assert isinstance(policy, IdentityMarkupPolicy)


def test_vendor_markup_policy_for_map_on_opt() -> None:
    """map_on_opt → make_map_on_opt_markup_policy(config)."""
    from parsers.base_parser.markup_policy import MapOnOptMarkupPolicy

    @register_vendor(_UNIQUE + '_8', markup_policy='map_on_opt')
    class MapOptVendor(_FakeBaseParser):  # noqa: WPS431
        pass

    config = MagicMock()
    policy = vendor_markup_policy_for(MapOptVendor, config)
    assert isinstance(policy, MapOnOptMarkupPolicy)


def test_vendor_markup_policy_for_recommended_or_map() -> None:
    """recommended_or_map → RecommendedOrMapMarkupPolicy.from_config(config)."""
    from parsers.base_parser.markup_policy import RecommendedOrMapMarkupPolicy

    @register_vendor(_UNIQUE + '_9', markup_policy='recommended_or_map')
    class RecMapVendor(_FakeBaseParser):  # noqa: WPS431
        pass

    config = MagicMock()
    policy = vendor_markup_policy_for(RecMapVendor, config)
    assert isinstance(policy, RecommendedOrMapMarkupPolicy)


def test_all_vendors_from_registry_populates_when_empty() -> None:
    """Пустой реестр: _ensure_vendors_imported() импортирует модули вендоров и заполняет реестр."""
    saved = dict(_registry)
    try:
        clear_registry()
        with patch('parsers.registry._VENDORS_TO_IMPORT', ('tests.test_parsers._registry_import_vendor',)):
            vendor_classes = {parser for parser, _ in all_vendors_from_registry()}
    finally:
        _registry.clear()
        _registry.update(saved)

    from tests.test_parsers._registry_import_vendor import ImportTestVendor

    assert ImportTestVendor in vendor_classes


def test_ensure_vendors_imported_short_circuits() -> None:
    """_ensure_vendors_imported() при заполненном реестре ничего не импортирует."""
    from parsers.registry import _ensure_vendors_imported

    @register_vendor(_UNIQUE + '_10')
    class PresentParser(_FakeBaseParser):  # noqa: WPS431
        pass

    with patch('parsers.registry.importlib.import_module') as mock_import:
        _ensure_vendors_imported()
    mock_import.assert_not_called()


def test_config_uses_valid_make_config() -> None:
    """make_config вернул ParseConfiguration — используется он, а не fallback."""
    from parsers.base_parser.base_parser_config import make_parse_config

    @register_vendor(_UNIQUE + '_11')
    class WithMakeConfig(_FakeBaseParser):  # noqa: WPS431
        @classmethod
        def make_config(cls):  # type: ignore[no-untyped-def]
            return make_parse_config(cls.parser_params())

    config = {parser: cfg for parser, cfg in all_vendors_from_registry()}[WithMakeConfig]
    assert config.supplier.folder_name == 'fake_vendor'


def test_vendor_without_config_source_is_skipped() -> None:
    """Вендор без make_config, module-config и parser_params исключается."""

    @register_vendor(_UNIQUE + '_12')
    class NoConfigSource:  # noqa: WPS431
        """Вендор без источников конфига."""

        @classmethod
        def supplier_folder_name(cls) -> str:
            return 'no_config'

        @classmethod
        def display_name(cls) -> str:
            return ''

    assert all(parser_cls is not NoConfigSource for parser_cls, _ in all_vendors_from_registry())


def test_vendor_with_bad_parser_params_is_skipped() -> None:
    """parser_params вернул не ParserParams — вендор исключается."""

    @register_vendor(_UNIQUE + '_13')
    class BadParamsParser(_FakeBaseParser):  # noqa: WPS431
        @classmethod
        def parser_params(cls) -> str:
            return 'not params'

    assert all(parser_cls is not BadParamsParser for parser_cls, _ in all_vendors_from_registry())


def test_vendor_markup_policy_for_custom_class() -> None:
    """_markup_policy_type — класс MarkupPolicy → make_markup_policy(config)."""
    from parsers.base_parser.markup_policy import MarkupPolicy

    @register_vendor(_UNIQUE + '_14', markup_policy=MarkupPolicy)
    class CustomPolicyVendor(_FakeBaseParser):  # noqa: WPS431
        pass

    config = MagicMock()
    policy = vendor_markup_policy_for(CustomPolicyVendor, config)
    assert isinstance(policy, MarkupPolicy)


def test_vendor_markup_policy_for_unknown_type_returns_none() -> None:
    """_markup_policy_type — тип, но не MarkupPolicy → None."""

    @register_vendor(_UNIQUE + '_15', markup_policy=int)
    class UnknownPolicyVendor(_FakeBaseParser):  # noqa: WPS431
        pass

    assert vendor_markup_policy_for(UnknownPolicyVendor, MagicMock()) is None


def test_clear_registry_empties_dict() -> None:
    """clear_registry() очищает _registry."""
    # Save and restore the real vendor entries to avoid breaking other tests.
    saved = dict(_registry)
    try:
        clear_registry()
        assert len(_registry) == 0

        @register_vendor('_tmp_unique_for_clear_test')
        class TmpParser(_FakeBaseParser):  # noqa: WPS431
            pass

        assert len(_registry) == 1
        clear_registry()
        assert len(_registry) == 0
    finally:
        # Restore real vendors so other tests in the same worker work.
        _registry.update(saved)
