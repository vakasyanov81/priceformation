"""Адаптер готового листа к существующему XLSX-писателю."""

from parsers.writer.templates.group_output import GroupOutput, WriteColors, WriteColumns
from parsers.writer.templates.iwrite_template import IWriteTemplate


class SheetTemplate(IWriteTemplate):
    """Использует настройки плана; групповые фильтры уже применены к модели."""

    def __init__(self, file_name: str, settings: GroupOutput) -> None:
        super().__init__()
        self._file_name = file_name
        self._settings = settings

    def columns(self) -> WriteColumns:
        return self._settings.columns

    def colors(self) -> WriteColors:
        return self._settings.formatting

    def get_file_name(self) -> str:
        return self._file_name

    def resolve_file_name(self, _current_date: str) -> str:
        """Имя плана уже разрешено, повторная подстановка запрещена."""
        return self._file_name

    def get_sheet_name(self) -> str:
        return self._settings.sheet_name
