"""Data types and mutant name helpers."""

from dataclasses import dataclass

CLASS_SEPARATOR = "\u01c1"
MUTANT_MARKER = "__mutmut_"
INTERESTING_STATUSES = frozenset(
    {
        "survived",
        "no tests",
        "timeout",
        "suspicious",
        "segfault",
    },
)
STATUS_BY_EXIT_CODE = {
    1: "killed",
    3: "killed",
    0: "survived",
    5: "no tests",
    2: "check was interrupted by user",
    33: "no tests",
    34: "skipped",
    35: "suspicious",
    36: "timeout",
    37: "caught by type check",
    24: "timeout",
    152: "timeout",
    255: "timeout",
    -24: "timeout",
    -11: "segfault",
    -9: "segfault",
}
SUMMARY_STATUS_ORDER = (
    "killed",
    "survived",
    "no tests",
    "timeout",
    "suspicious",
    "skipped",
    "segfault",
    "caught by type check",
    "check was interrupted by user",
    "not checked",
)


@dataclass(frozen=True)
class RawMutant:
    """One mutant as stored under mutants/."""

    name: str
    source_path: str
    exit_code: int | None
    tests: tuple[str, ...]
    orig_source: str
    mutant_source: str


@dataclass(frozen=True)
class MutantRecord:
    """Classified mutant ready for reporting."""

    name: str
    status: str
    source_path: str
    function: str
    kind: str
    change: str
    tests: tuple[str, ...]
    diff: str


@dataclass(frozen=True)
class CountRow:
    """A grouped counter row."""

    key: str
    count: int


@dataclass(frozen=True)
class ChangeRow:
    """Survivors that share the same source change."""

    kind: str
    change: str
    count: int
    functions: tuple[str, ...]


@dataclass(frozen=True)
class Analysis:
    """Deterministic mutmut statistics."""

    summary: tuple[tuple[str, int], ...]
    mutation_score: float
    by_file: tuple[CountRow, ...]
    by_function: tuple[CountRow, ...]
    by_kind: tuple[CountRow, ...]
    by_change: tuple[ChangeRow, ...]
    interesting: tuple[MutantRecord, ...]


def status_from_exit_code(exit_code: int | None) -> str:
    """Map a mutmut pytest exit code to a status name."""
    if exit_code is None:
        return "not checked"
    return STATUS_BY_EXIT_CODE.get(exit_code, "suspicious")


def function_from_mutant_name(mutant_name: str) -> str:
    """Human-readable function or Class.method from a mutant key."""
    mangled = mutant_name.partition(MUTANT_MARKER)[0]
    _, _, tail = mangled.rpartition(".")
    if CLASS_SEPARATOR in tail:
        parts = tail.split(CLASS_SEPARATOR)
        return f"{parts[1]}.{parts[2]}"
    if tail.startswith("x_"):
        return tail[2:]
    return tail


def mutant_index(mutant_name: str) -> int:
    """Numeric suffix of a mutant key."""
    suffix = mutant_name.rpartition(MUTANT_MARKER)[2]
    if suffix.isdigit():
        return int(suffix)
    return 0


def mangled_name(mutant_name: str) -> str:
    """Function key used in mutmut-stats.json."""
    return mutant_name.partition(MUTANT_MARKER)[0]
