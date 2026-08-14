"""Classify a mutant diff into a kind and a short change label."""

import re
from difflib import SequenceMatcher

_OPERATOR_PAIRS = (
    ("is not", "is"),
    ("not in", "in"),
    ("is", "is not"),
    ("in", "not in"),
    ("==", "!="),
    ("!=", "=="),
    ("<=", "<"),
    (">=", ">"),
    ("<", "<="),
    (">", ">="),
    ("and", "or"),
    ("or", "and"),
    ("+=", "="),
    ("+", "-"),
    ("-", "+"),
    ("*", "/"),
    ("/", "*"),
)
_METHOD_PAIRS = (
    ("lower", "upper"),
    ("upper", "lower"),
    ("lstrip", "rstrip"),
    ("rstrip", "lstrip"),
    ("find", "rfind"),
    ("rfind", "find"),
    ("ljust", "rjust"),
    ("rjust", "ljust"),
    ("index", "rindex"),
    ("rindex", "index"),
    ("removeprefix", "removesuffix"),
    ("removesuffix", "removeprefix"),
    ("partition", "rpartition"),
    ("rpartition", "partition"),
    ("split", "rsplit"),
    ("rsplit", "split"),
)
_KEYWORD_PAIRS = (
    ("break", "return"),
    ("continue", "break"),
    ("True", "False"),
    ("False", "True"),
    ("deepcopy", "copy"),
)
_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")
_QUOTED = re.compile(r'["\']([^"\']*)["\']')
_NAME = re.compile(r"\b\w+\b")
_KIND_OPERATOR = "operator"
_KIND_METHOD = "method_swap"
_KIND_KEYWORD = "keyword"
_NONE = "None"
_ASSIGN_NONE = "= None"


def classify_diff(diff: str) -> tuple[str, str]:
    """Return (kind, change) for a unified diff."""
    old_text, new_text = _changed_texts(diff)
    if not old_text and not new_text:
        return ("unknown", "")
    return _classify_texts(old_text, new_text)


def _classify_texts(old_text: str, new_text: str) -> tuple[str, str]:
    detectors = (
        _pair_from_texts,
        _string_wrap,
        _string_case,
        _assignment_to_none,
        _name_to_none,
        _removed_not,
    )
    for detector in detectors:
        found = detector(old_text, new_text)
        if found is not None:
            return found
    old_bit, new_bit = _first_delta(old_text, new_text)
    detected = _detect_kind(old_bit, new_bit)
    if detected is not None:
        return detected
    return ("other", _arrow(old_bit, new_bit))


def _changed_texts(diff: str) -> tuple[str, str]:
    removed = _diff_side(diff, prefix="-")
    added = _diff_side(diff, prefix="+")
    return (removed, added)


def _diff_side(diff: str, prefix: str) -> str:
    skip = f"{prefix}{prefix}{prefix}"
    collected: list[str] = []
    for line in diff.splitlines():
        if line.startswith(skip) or line.startswith("@@"):
            continue
        if line.startswith(prefix):
            collected.append(line[1:].strip())
    return "\n".join(collected)


def _first_delta(old_text: str, new_text: str) -> tuple[str, str]:
    matcher = SequenceMatcher(a=old_text, b=new_text, autojunk=False)
    for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        return (old_text[old_start:old_end].strip(), new_text[new_start:new_end].strip())
    return (old_text.strip(), new_text.strip())


def _pair_from_texts(old_text: str, new_text: str) -> tuple[str, str] | None:
    tables = (
        (_KIND_OPERATOR, _OPERATOR_PAIRS),
        (_KIND_METHOD, _METHOD_PAIRS),
        (_KIND_KEYWORD, _KEYWORD_PAIRS),
    )
    for kind, pairs in tables:
        found = _first_matching_pair(old_text, new_text, kind, pairs)
        if found is not None:
            return found
    return None


def _first_matching_pair(
    old_text: str,
    new_text: str,
    kind: str,
    pairs: tuple[tuple[str, str], ...],
) -> tuple[str, str] | None:
    for left, right in pairs:
        if _replaced_once(old_text, left, right) == new_text:
            return (kind, _arrow(left, right))
    return None


def _replaced_once(text: str, old: str, new: str) -> str:
    if old[0].isalnum() or " " in old:
        pattern = rf"\b{re.escape(old)}\b"
        return re.sub(pattern, new, text, count=1)
    return text.replace(old, new, 1)


def _detect_kind(old_bit: str, new_bit: str) -> tuple[str, str] | None:
    detectors = (
        _string_wrap,
        _string_case,
        _number_plus_one,
        _to_none,
        _none_to_empty,
    )
    for detector in detectors:
        found = detector(old_bit, new_bit)
        if found is not None:
            return found
    return None


def _string_wrap(old_bit: str, new_bit: str) -> tuple[str, str] | None:
    if new_bit.replace("XX", "") != old_bit or "XX" not in new_bit:
        return None
    match = re.search(r"XX.+?XX", new_bit)
    if match is None:
        return ("string_wrap", _arrow(old_bit, new_bit))
    wrapped = match.group(0)
    return ("string_wrap", _arrow(wrapped[2:-2], wrapped))


def _string_case(old_bit: str, new_bit: str) -> tuple[str, str] | None:
    if old_bit.lower() != new_bit.lower() or old_bit == new_bit:
        return None
    old_quoted = _QUOTED.findall(old_bit)
    new_quoted = _QUOTED.findall(new_bit)
    if old_quoted and new_quoted:
        return ("string_case", _arrow(old_quoted[0], new_quoted[0]))
    return ("string_case", _arrow(old_bit, new_bit))


def _assignment_to_none(old_text: str, new_text: str) -> tuple[str, str] | None:
    new_stripped = new_text.strip()
    if not new_stripped.endswith(_ASSIGN_NONE):
        return None
    left_side = new_stripped[: -len(_ASSIGN_NONE)].rstrip()
    old_stripped = old_text.strip()
    prefix = f"{left_side} ="
    if not old_stripped.startswith(prefix):
        return None
    right_side = old_stripped[len(prefix) :].strip()
    if right_side == _NONE:
        return None
    return ("to_none", _arrow(right_side, _NONE))


def _name_to_none(old_text: str, new_text: str) -> tuple[str, str] | None:
    if _NONE not in new_text:
        return None
    for match in _NAME.finditer(old_text):
        replaced = f"{old_text[: match.start()]}{_NONE}{old_text[match.end() :]}"
        if replaced == new_text:
            return ("to_none", _arrow(match.group(0), _NONE))
    return None


def _removed_not(old_text: str, new_text: str) -> tuple[str, str] | None:
    if old_text.replace("not ", "", 1) == new_text:
        return ("keyword", _arrow("not", ""))
    return None


def _number_plus_one(old_bit: str, new_bit: str) -> tuple[str, str] | None:
    if not _NUMBER.match(old_bit) or not _NUMBER.match(new_bit):
        return None
    if float(new_bit) == float(old_bit) + 1:
        return ("number", _arrow(old_bit, new_bit))
    return None


def _to_none(old_bit: str, new_bit: str) -> tuple[str, str] | None:
    if new_bit == _NONE and old_bit != _NONE:
        return ("to_none", _arrow(old_bit, new_bit))
    return None


def _none_to_empty(old_bit: str, new_bit: str) -> tuple[str, str] | None:
    if old_bit == _NONE and new_bit.strip('\'"') == "":
        return ("none_to_empty", _arrow(old_bit, new_bit))
    return None


def _arrow(old_bit: str, new_bit: str) -> str:
    left = old_bit or "∅"
    right = new_bit or "∅"
    return f"{left} → {right}"
