"""Ошибки порядка инициализации XLSX-драйвера."""


class WorkbookNotInitializedError(RuntimeError):
    """Книга ещё не создана."""

    def __init__(self) -> None:
        super().__init__('workbook is not initialized')


class WorksheetNotInitializedError(RuntimeError):
    """Лист ещё не выбран."""

    def __init__(self) -> None:
        super().__init__('worksheet is not initialized')
