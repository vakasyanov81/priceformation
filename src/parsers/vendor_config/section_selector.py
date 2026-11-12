"""Выбор товаров по ключевым словам раздела верхнего уровня."""

from dataclasses import dataclass

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig, as_config_object
from parsers.vendor_config.fields import read_str_list, read_text


@dataclass(frozen=True, slots=True)
class SectionSelector:
    """Колонка названия и подстроки заголовка без учёта регистра."""

    column: str
    keywords: tuple[str, ...]

    @classmethod
    def from_payload(cls, payload: RawConfig, where: str) -> SectionSelector | None:
        """Отсутствующий фильтр сохраняет прежний разбор всех строк."""
        if 'section_selector' not in payload:
            return None
        location = f'{where} → section_selector'
        settings = as_config_object(payload['section_selector'], location)
        keywords = read_str_list(settings, 'keywords', location)
        if not keywords or any(not keyword.strip() for keyword in keywords):
            raise ConfigValidationError(f'{location} → keywords: требуется непустой список непустых строк')
        normalized = tuple(keyword.strip().casefold() for keyword in keywords)
        return cls(read_text(settings, 'column', location), normalized)

    def matches(self, heading: str) -> bool:
        """Достаточно одного ключевого слова в заголовке корневого раздела."""
        return any(keyword in heading.casefold() for keyword in self.keywords)
