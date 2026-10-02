"""Layer checks: parsers do not import cfg, domain stays pure, config comes from the provider."""

from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2] / 'src'
_PARSERS_ROOT = _SRC_ROOT / 'parsers'
_DOMAIN_ROOT = _SRC_ROOT / 'domain'
_CONFIG_MODULE = _PARSERS_ROOT / 'base_parser' / 'base_parser_config.py'
_CFG_MARKERS = ('from cfg', 'import cfg')
_DEMETER_CHAIN = 'parse_config.parser_params'
_MAIN_CONFIG_MARKERS = ('MainConfig', 'MainCfg', 'cfg.main', 'get_parse_paths')
_DOMAIN_FORBIDDEN = ('from core', 'import core', 'infrastructure', 'parsers', 'cfg')


def test_parsers_do_not_import_cfg() -> None:
    offenders = [
        str(path.relative_to(_PARSERS_ROOT))
        for path in _PARSERS_ROOT.rglob('*.py')
        if any(marker in path.read_text(encoding='utf-8') for marker in _CFG_MARKERS)
    ]
    assert not offenders


def test_parser_params_chain_only_in_config() -> None:
    offenders = []
    for path in _PARSERS_ROOT.rglob('*.py'):
        if path.resolve() == _CONFIG_MODULE.resolve():
            continue
        if _DEMETER_CHAIN in path.read_text(encoding='utf-8'):
            offenders.append(str(path.relative_to(_PARSERS_ROOT)))
    assert not offenders


def test_domain_has_no_infrastructure_imports() -> None:
    offenders = [
        str(path.relative_to(_DOMAIN_ROOT))
        for path in _DOMAIN_ROOT.rglob('*.py')
        if any(marker in path.read_text(encoding='utf-8') for marker in _DOMAIN_FORBIDDEN)
    ]
    assert not offenders


def test_no_module_refers_to_removed_main_config() -> None:
    offenders = [
        str(path.relative_to(_SRC_ROOT))
        for path in _SRC_ROOT.rglob('*.py')
        if any(marker in path.read_text(encoding='utf-8') for marker in _MAIN_CONFIG_MARKERS)
    ]
    assert not offenders
