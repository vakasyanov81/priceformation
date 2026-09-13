"""Сборка графа зависимостей приложения в ServiceProvider."""

from parsers.base_parser.base_parser import make_parser
from parsers.common_price import GrouperFactory, ParserFactory
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.common_price_output import WriteDriverFactory, XlsWriterFactory
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver
from services.service_provider import ServiceProvider


def configure_services() -> None:
    """Зарегистрировать фабрики приложения. Повторный вызов безопасен."""
    ServiceProvider.register(ParserFactory, lambda: make_parser)
    ServiceProvider.register(GrouperFactory, lambda: CommonPriceGrouper)
    ServiceProvider.register(XlsWriterFactory, lambda: XlsWriter)
    ServiceProvider.register(WriteDriverFactory, lambda: XlsxWriterDriver)


def ensure_services_configured() -> None:
    """Собрать граф, если контейнер ещё пуст (прямой вызов machine_json)."""
    if not ServiceProvider.is_configured():
        configure_services()
