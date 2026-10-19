"""Слияние моделей в ключе группировки: модель с лишними словами — та же, что и короткая.

Поставщики пишут модель по-разному: ``Gravity`` / ``GRAVITY SUV``, ``G075`` / ``Ice Guard G075``,
``НК-241 GRANT`` / ``Grant (НК-241)``. Ключ ``clear_model`` склеивает слова в строку, и такие варианты
в разные группы. Здесь модели с одним ядром ключа (всё, кроме модели) сравниваются по наборам слов:
короткая модель присоединяется к ближайшей по числу слов длинной, куда входит целиком, и так по цепочке:
``Gravity`` → ``Gravity SUV`` → ``Gravity SUV PS-9``. Если ближайших несколько и они равны по размеру
(``G075`` входит и в ``Ice Guard G075``, и в ``iceGuard Studless G075``), неясно, какая из них нужна, —
ничего не склеиваем. Слова, написанные раздельно (``ice guard``), входят в слитное слово другой модели
(``iceGuard``), поэтому ``Ice Guard G075`` считается вложенной в ``iceGuard Studless G075``.
"""

from collections.abc import Iterable
from functools import partial

Tokens = frozenset[str]
ModelEntry = tuple[str, Tokens]
CanonicalKeys = dict[Tokens, str]


def merge_models(entries: Iterable[ModelEntry]) -> dict[str, str]:
    """Карта «ключ модели → канонический ключ модели» для моделей одного ядра ключа."""
    token_sets = {model_key: tokens for model_key, tokens in entries if model_key and tokens}
    canonical = _canonical_keys(token_sets)
    target = partial(_target_tokens, canonical=canonical)
    return {model_key: canonical[target(tokens)] for model_key, tokens in token_sets.items()}


def _canonical_keys(token_sets: dict[str, Tokens]) -> CanonicalKeys:
    """Один ключ на набор слов: наименьший по порядку, чтобы результат не зависел от порядка прайсов."""
    canonical: CanonicalKeys = {}
    for model_key, tokens in sorted(token_sets.items()):
        canonical.setdefault(tokens, model_key)
    return canonical


def _target_tokens(tokens: Tokens, canonical: CanonicalKeys) -> Tokens:
    """Набор слов, к которому присоединяется модель: ближайшее надмножество по цепочке, иначе свой."""
    nearest = _nearest_superset(tokens, canonical)
    return tokens if nearest is None else _target_tokens(nearest, canonical)


def _nearest_superset(tokens: Tokens, canonical: CanonicalKeys) -> Tokens | None:
    """Ближайшая модель, куда входит `tokens`; None, если её нет или ближайших несколько."""
    supersets = [other for other in canonical if _is_inside(tokens, other)]
    nearest = [other for other in supersets if not _contains_any(other, supersets)]
    return nearest[0] if len(nearest) == 1 else None


def _contains_any(outer: Tokens, candidates: list[Tokens]) -> bool:
    """В `outer` входит хотя бы одна другая модель из `candidates`."""
    return any(_is_inside(inner, outer) for inner in candidates if inner != outer)


def _split_pair(word: str, unmatched: set[str]) -> tuple[str, str] | None:
    """Две раздельные части из `unmatched`, дающие `word` при склейке."""
    for first in unmatched:
        second = word.removeprefix(first)
        if second not in {word, first} and second in unmatched:
            return first, second
    return None


def _is_inside(tokens: Tokens, other: Tokens) -> bool:
    """Все слова `tokens` есть в `other`, а раздельно написанные слитно (`ice`+`guard` = `iceguard`) входят в него."""
    if tokens < other:
        return True
    unmatched = set(tokens - other)
    joined_words = other - tokens
    for word in joined_words:
        pair = _split_pair(word, unmatched)
        if pair:
            unmatched.difference_update(pair)
    return not unmatched and bool(joined_words)
