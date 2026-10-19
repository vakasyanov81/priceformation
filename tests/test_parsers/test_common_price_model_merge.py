"""tests for model merge by token sets."""

from parsers.common_price_model_merge import ModelEntry, merge_models


def _entry(model: str) -> ModelEntry:
    return model.replace(' ', ''), frozenset(model.split())


def _entries(*models: str) -> list[ModelEntry]:
    return [_entry(model) for model in models]


def test_short_model_joins_the_only_longer_one() -> None:
    merged = merge_models(_entries('g075', 'ice guard g075'))
    assert merged['g075'] == merged['iceguardg075'] == 'iceguardg075'


def test_ambiguous_short_model_is_left_alone() -> None:
    """`gravity` входит и в `gravity suv`, и в `gravity suv ps9`: возможно, это разные модели."""
    merged = merge_models(_entries('gravity', 'gravity suv', 'gravity suv ps9'))
    assert merged['gravity'] == 'gravity'
    assert merged['gravitysuv'] == merged['gravitysuvps9'] == 'gravitysuvps9'


def test_same_words_different_order_merge() -> None:
    merged = merge_models(_entries('hk241 grant', 'grant hk241'))
    assert merged['hk241grant'] == merged['granthk241'] == 'granthk241'


def test_unrelated_models_stay_apart() -> None:
    merged = merge_models(_entries('gravity', 'winter drive'))
    assert merged == {'gravity': 'gravity', 'winterdrive': 'winterdrive'}


def test_models_without_words_are_skipped() -> None:
    entries = [('', frozenset[str]()), *_entries('x')]
    assert merge_models(entries) == {'x': 'x'}
