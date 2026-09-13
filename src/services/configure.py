"""Сборка графа зависимостей приложения в ServiceProvider."""

from parsers.base_parser.base_parser import make_parser
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.common_price_output import WriteDriverFactory, XlsWriterFactory
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver
from services.doubles_service import DoublesService
from services.parse_orchestrator import GrouperFactory, ParseOrchestrator, ParserFactory
from services.price_report import PriceReportService
from services.service_provider import ServiceProvider
from services.zapaska_service import ZapaskaService


def configure_services() -> None:
    """Зарегистрировать фабрики и сервисы приложения. Повторный вызов безопасен."""
    ServiceProvider.register(ParserFactory, lambda: make_parser)
    ServiceProvider.register(GrouperFactory, lambda: CommonPriceGrouper)
    ServiceProvider.register(XlsWriterFactory, lambda: XlsWriter)
    ServiceProvider.register(WriteDriverFactory, lambda: XlsxWriterDriver)
    ServiceProvider.register(ParseOrchestrator, ParseOrchestrator)
    ServiceProvider.register(PriceReportService, PriceReportService)
    ServiceProvider.register(DoublesService, DoublesService)
    ServiceProvider.register(ZapaskaService, ZapaskaService)


def ensure_services_configured() -> None:
    """Собрать граф, если контейнер ещё пуст (прямой вызов machine_json)."""
    if not ServiceProvider.is_configured():
        configure_services()
