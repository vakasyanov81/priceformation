"""Тесты сборки графа зависимостей приложения."""

from parsers.base_parser.base_parser import make_parser
from parsers.common_price import GrouperFactory, ParserFactory
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.common_price_output import WriteDriverFactory, XlsWriterFactory
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver
from services.configure import configure_services, ensure_services_configured
from services.service_provider import ServiceProvider


def test_configure_registers_factories() -> None:
    """configure_services регистрирует все фабрики приложения."""
    ServiceProvider.clear()
    configure_services()
    assert ServiceProvider.is_configured()
    assert ServiceProvider.resolve(ParserFactory) is make_parser
    assert ServiceProvider.resolve(GrouperFactory) is CommonPriceGrouper
    assert ServiceProvider.resolve(XlsWriterFactory) is XlsWriter
    assert ServiceProvider.resolve(WriteDriverFactory) is XlsxWriterDriver


def test_configure_is_idempotent() -> None:
    """повторный configure_services не ломает регистрацию."""
    ServiceProvider.clear()
    configure_services()
    configure_services()
    assert ServiceProvider.resolve(ParserFactory) is make_parser
    assert ServiceProvider.resolve(GrouperFactory) is CommonPriceGrouper


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
