"""Layer checks: domain stays pure, infrastructure knows no parsers, config comes from the provider."""

from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parent.parent / 'src'
_PARSERS_ROOT = _SRC_ROOT / 'parsers'
_DOMAIN_ROOT = _SRC_ROOT / 'domain'
_INFRASTRUCTURE_ROOT = _SRC_ROOT / 'infrastructure'
_LEGACY_CORE_ROOT = _SRC_ROOT / 'core'
_CONFIG_MODULE = _PARSERS_ROOT / 'base_parser' / 'base_parser_config.py'
_CFG_MARKERS = ('from cfg', 'import cfg')
_DEMETER_CHAIN = 'parse_config.parser_params'
_MAIN_CONFIG_MARKERS = ('MainConfig', 'MainCfg', 'cfg.main', 'get_parse_paths')
_DOMAIN_FORBIDDEN = (
    'from infrastructure',
    'import infrastructure',
    'from parsers',
    'import parsers',
    'from services',
    'import services',
    'from cfg',
    'import cfg',
)
_INFRASTRUCTURE_FORBIDDEN = ('import parsers', 'from parsers', 'import cfg', 'from cfg')


def _offenders(root: Path, markers: tuple[str, ...]) -> list[str]:
    """Файлы под root, где встречается хотя бы один маркер."""
    return [
        str(path.relative_to(root))
        for path in root.rglob('*.py')
        if any(marker in path.read_text(encoding='utf-8') for marker in markers)
    ]


def test_parsers_do_not_import_cfg() -> None:
    assert not _offenders(_PARSERS_ROOT, _CFG_MARKERS)


def test_parser_params_chain_only_in_config() -> None:
    offenders = []
    for path in _PARSERS_ROOT.rglob('*.py'):
        source = path.read_text(encoding='utf-8')
        if path.resolve() != _CONFIG_MODULE.resolve() and _DEMETER_CHAIN in source:
            offenders.append(str(path.relative_to(_PARSERS_ROOT)))
    assert not offenders


def test_domain_has_no_infrastructure_imports() -> None:
    assert not _offenders(_DOMAIN_ROOT, _DOMAIN_FORBIDDEN)


def test_infrastructure_ignores_parsers_and_cfg() -> None:
    assert not _offenders(_INFRASTRUCTURE_ROOT, _INFRASTRUCTURE_FORBIDDEN)


def test_no_module_refers_to_removed_main_config() -> None:
    assert not _offenders(_SRC_ROOT, _MAIN_CONFIG_MARKERS)


def test_legacy_core_package_is_gone() -> None:
    """core/ разделён на domain/ и infrastructure/, пакет удалён."""
    assert not _LEGACY_CORE_ROOT.exists()
