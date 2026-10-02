"""Маркеры архитектуры, которые нельзя выразить контрактами import-linter.

Импортные правила слоёв живут в `[tool.importlinter]` (uv run lint-imports):
    - Слои: cfg/services -> parsers -> infrastructure -> domain
    - Domain не зависит от инфраструктуры, парсеров, сервисов и композиционного корня
    - Инфраструктура не зависит от прикладных слоёв
    - Парсеры не знают про композиционный корень и сервисы
    - Сервисы не зависят от композиционного корня
"""

from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parent.parent / 'src'
_PARSERS_ROOT = _SRC_ROOT / 'parsers'
_CONFIG_MODULE = _PARSERS_ROOT / 'base_parser' / 'base_parser_config.py'
_LEGACY_CORE_ROOT = _SRC_ROOT / 'core'
_DEMETER_CHAIN = 'parse_config.parser_params'
_MAIN_CONFIG_MARKERS = ('MainConfig', 'MainCfg', 'cfg.main', 'get_parse_paths')


def _offenders(root: Path, markers: tuple[str, ...]) -> list[str]:
    """Файлы под root, где встречается хотя бы один маркер."""
    return [
        str(path.relative_to(root))
        for path in root.rglob('*.py')
        if any(marker in path.read_text(encoding='utf-8') for marker in markers)
    ]


def test_parser_params_chain_only_in_config() -> None:
    """Цепочка parse_config.parser_params допустима только в конфиге парсера."""
    offenders = []
    for path in _PARSERS_ROOT.rglob('*.py'):
        source = path.read_text(encoding='utf-8')
        if path.resolve() != _CONFIG_MODULE.resolve() and _DEMETER_CHAIN in source:
            offenders.append(str(path.relative_to(_PARSERS_ROOT)))
    assert not offenders


def test_no_module_refers_to_removed_main_config() -> None:
    assert not _offenders(_SRC_ROOT, _MAIN_CONFIG_MARKERS)


def test_legacy_core_package_is_gone() -> None:
    """core/ разделён на domain/ и infrastructure/, пакет удалён."""
    assert not _LEGACY_CORE_ROOT.exists()
