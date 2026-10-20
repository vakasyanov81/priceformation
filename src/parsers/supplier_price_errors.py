"""Ошибки загрузки прайсов поставщиков."""

from domain.exceptions import CoreExceptionError


class SupplierPricesMappingError(CoreExceptionError):
    """JSON-карта ИД или sup_code → путь к прайсу некорректна."""


class InvalidPriceExtensionError(CoreExceptionError):
    """Расширение файла не xls, xlsx, json или zip, либо zip-архив повреждён."""


class UnknownSupplierCodeError(CoreExceptionError):
    """ИД или sup_code поставщика нет в каталоге."""


class SupplierPriceFileNotFoundError(CoreExceptionError):
    """Исходный файл прайса не найден."""


class SupplierPriceFileNameError(CoreExceptionError):
    """Имя файла не подходит под маски поставщика, и переименовать его в прайс нельзя."""
