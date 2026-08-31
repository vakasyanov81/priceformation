"""Ошибки загрузки прайсов поставщиков."""

from core.exceptions import CoreExceptionError


class SupplierPricesMappingError(CoreExceptionError):
    """JSON-карта ИД или sup_code → путь к прайсу некорректна."""


class InvalidPriceExtensionError(CoreExceptionError):
    """Расширение файла не xls и не xlsx."""


class UnknownSupplierCodeError(CoreExceptionError):
    """ИД или sup_code поставщика нет в каталоге."""


class SupplierPriceFileNotFoundError(CoreExceptionError):
    """Исходный файл прайса не найден."""
