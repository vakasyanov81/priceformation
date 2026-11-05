"""Модель позиции для ключа группировки: очистка и разбор на слова."""

from parsers.strategies.normalize import replace_homoglyphs

_KNOWN_MODEL_PREFIXES = ('кама', 'kama')
_PREFIX_SEPARATORS = '- '
# Скобки, дефисы и апострофы поставщики расставляют по-разному (`Breeze (НК-132)`, `AE-51`/`AE51`, `N'Blue`/`Nblue`).
_MODEL_PUNCTUATION = str.maketrans('', '', "()-'\u2019`")
# Кириллица, оставшаяся после гомоглифов, — транслитерация латинского названия (`Бел-298` = `BEL-298`).
_TRANSLIT = str.maketrans(
    {
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'y',
        'л': 'l',
        'н': 'n',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'у': 'u',
        'ф': 'f',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'sch',
        'ы': 'y',
        'э': 'e',
        'ю': 'yu',
        'я': 'ya',
        'ё': 'e',
        'ъ': '',
        'ь': '',
    }
)


def clear_model(
    model: str | None,
    manufacturer: str | None = None,
    brand: str | None = None,
) -> str:
    """Очистка модели: регистр, пробелы, скобки, дефисы, апострофы, префикс бренда; двойники → латиница."""
    if not model:
        return ''
    normalized = model.lower()
    for prefix in _model_prefixes(manufacturer, brand):
        normalized = _lstrip_brand_prefix(normalized, prefix)
    return replace_homoglyphs(normalized.replace(' ', '').translate(_MODEL_PUNCTUATION))


def model_tokens(
    model: str | None,
    manufacturer: str | None = None,
    brand: str | None = None,
) -> frozenset[str]:
    """Слова модели без префикса бренда, скобок, дефисов и апострофов; двойники → латиница."""
    if not model:
        return frozenset()
    normalized = model.lower()
    for prefix in _model_prefixes(manufacturer, brand):
        normalized = _lstrip_brand_prefix(normalized, prefix)
    words = (_latinize(word.translate(_MODEL_PUNCTUATION)) for word in normalized.split())
    return frozenset(word for word in words if word)


def _latinize(word: str) -> str:
    """Слово для сравнения моделей: гомоглифы и транслитерация кириллицы → латиница."""
    return replace_homoglyphs(word).translate(_TRANSLIT)


def _lstrip_brand_prefix(model: str, prefix: str) -> str:
    """Убрать префикс бренда, если за ним разделитель или конец строки."""
    if not model.startswith(prefix):
        return model
    rest = model[len(prefix) :]
    if not rest:
        return ''
    if rest[0] in _PREFIX_SEPARATORS:
        return rest.lstrip(_PREFIX_SEPARATORS)
    return model


def _model_prefixes(manufacturer: str | None, brand: str | None) -> list[str]:
    """Префиксы бренда: известные и имена manufacturer/brand, длинные раньше."""
    names = (manufacturer, brand, *_KNOWN_MODEL_PREFIXES)
    unique = {name.lower().strip() for name in names if name}
    return sorted(unique, key=len, reverse=True)
