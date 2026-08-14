"""Build a unified diff for one mutant."""

import re
from difflib import unified_diff

from .models import CLASS_SEPARATOR, MUTANT_MARKER, RawMutant, function_from_mutant_name

_DEF_NAME = re.compile(
    rf"def (x_(?:\w+)|x{CLASS_SEPARATOR}\w+{CLASS_SEPARATOR}\w+){MUTANT_MARKER}(?:orig|\d+)",
)
_GENERATED_MARK = " # type: ignore # mutmut generated"


def make_diff(raw: RawMutant) -> str:
    """Unified diff of original vs mutated function body."""
    if not raw.orig_source or not raw.mutant_source:
        return ""
    orig_lines = _normalized_lines(raw.orig_source, raw.name)
    mutant_lines = _normalized_lines(raw.mutant_source, raw.name)
    return "\n".join(
        unified_diff(
            orig_lines,
            mutant_lines,
            fromfile=raw.source_path,
            tofile=raw.source_path,
            lineterm="",
        ),
    )


def _normalized_lines(source: str, mutant_name: str) -> list[str]:
    renamed = _rename_def(source, function_from_mutant_name(mutant_name))
    cleaned = renamed.replace(_GENERATED_MARK, "")
    return cleaned.strip("\n").split("\n")


def _rename_def(source: str, function_name: str) -> str:
    short_name = function_name.rsplit(".", maxsplit=1)[-1]

    def _replace(match: re.Match[str]) -> str:
        return f"def {short_name}"

    return _DEF_NAME.sub(_replace, source, count=1)
