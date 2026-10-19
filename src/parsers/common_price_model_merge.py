"""Слияние моделей в ключе группировки: модель с лишними словами — та же, что и короткая.

Поставщики пишут модель по-разному: ``Gravity`` / ``GRAVITY SUV``, ``G075`` / ``Ice Guard G075``,
``НК-241 GRANT`` / ``Grant (НК-241)``. Ключ ``clear_model`` склеивает слова в строку, и такие варианты
в разные группы. Здесь модели с одним ядром ключа (всё, кроме модели) сравниваются по наборам слов:
короткая модель присоединяется к длинной, если эта длинная — единственная, куда короткая входит целиком.
Если подходящих несколько (``Gravity`` входит и в ``Gravity SUV``, и в ``Gravity SUV PS-9``), модели
могут быть разными — ничего не склеиваем.
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
    """Набор слов, к которому присоединяется модель: единственный надмножество, иначе свой."""
    supersets = [other for other in canonical if tokens < other]
    return supersets[0] if len(supersets) == 1 else tokens
