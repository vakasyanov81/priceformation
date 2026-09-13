"""Тесты сборки графа зависимостей приложения."""

from parsers.base_parser.base_parser import make_parser
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.common_price_output import WriteDriverFactory, XlsWriterFactory
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver
from services.configure import configure_services, ensure_services_configured
from services.doubles_service import DoublesService
from services.parse_orchestrator import GrouperFactory, ParseOrchestrator, ParserFactory
from services.price_report import PriceReportService
from services.service_provider import ServiceProvider
from services.zapaska_service import ZapaskaService


def test_configure_registers_factories() -> None:
    """configure_services регистрирует все фабрики приложения."""
    ServiceProvider.clear()
    configure_services()
    assert ServiceProvider.is_configured()
    assert ServiceProvider.resolve(ParserFactory) is make_parser
    assert ServiceProvider.resolve(GrouperFactory) is CommonPriceGrouper
    assert ServiceProvider.resolve(XlsWriterFactory) is XlsWriter
    assert ServiceProvider.resolve(WriteDriverFactory) is XlsxWriterDriver


def test_configure_registers_services() -> None:
    """configure_services регистрирует сервисы оркестрации."""
    ServiceProvider.clear()
    configure_services()
    assert isinstance(ServiceProvider.resolve(ParseOrchestrator), ParseOrchestrator)
    assert isinstance(ServiceProvider.resolve(PriceReportService), PriceReportService)
    assert isinstance(ServiceProvider.resolve(DoublesService), DoublesService)
    assert isinstance(ServiceProvider.resolve(ZapaskaService), ZapaskaService)


def test_configure_is_idempotent() -> None:
    """повторный configure_services не ломает регистрацию."""
    ServiceProvider.clear()
    configure_services()
    configure_services()
    assert ServiceProvider.resolve(ParserFactory) is make_parser
    assert ServiceProvider.resolve(GrouperFactory) is CommonPriceGrouper
    assert isinstance(ServiceProvider.resolve(ParseOrchestrator), ParseOrchestrator)


def test_resolved_services_share_factory_instances() -> None:
    """singleton-сервисы разрешаются одним экземпляром."""
    ServiceProvider.clear()
    configure_services()
    assert ServiceProvider.resolve(ParseOrchestrator) is ServiceProvider.resolve(ParseOrchestrator)


def test_ensure_configures_empty_provider() -> None:
    """ensure_services_configured собирает пустой контейнер."""
    ServiceProvider.clear()
    ensure_services_configured()
    assert ServiceProvider.is_configured()


def test_ensure_skips_configured_provider() -> None:
    """ensure_services_configured не трогает уже собранный контейнер."""
    ServiceProvider.clear()
    configure_services()
    ensure_services_configured()
    assert ServiceProvider.resolve(ParserFactory) is make_parser
