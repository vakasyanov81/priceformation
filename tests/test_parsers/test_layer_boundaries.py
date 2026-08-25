"""Layer checks: parsers do not import cfg or walk ParseConfiguration internals."""

from pathlib import Path

_PARSERS_ROOT = Path(__file__).resolve().parents[2] / "src" / "parsers"
_CONFIG_MODULE = _PARSERS_ROOT / "base_parser" / "base_parser_config.py"
_CFG_MARKERS = ("from cfg", "import cfg")
_DEMETER_CHAIN = "parse_config.parser_params"


def test_parsers_do_not_import_cfg() -> None:
    offenders = [
        str(path.relative_to(_PARSERS_ROOT))
        for path in _PARSERS_ROOT.rglob("*.py")
        if any(marker in path.read_text(encoding="utf-8") for marker in _CFG_MARKERS)
    ]
    assert not offenders


def test_parser_params_chain_only_in_config() -> None:
    offenders = []
    for path in _PARSERS_ROOT.rglob("*.py"):
        if path.resolve() == _CONFIG_MODULE.resolve():
            continue
        if _DEMETER_CHAIN in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(_PARSERS_ROOT)))
    assert not offenders
