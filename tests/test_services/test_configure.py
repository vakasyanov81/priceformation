"""Тесты сборки графа зависимостей приложения."""

from unittest.mock import MagicMock, patch

from domain.config_context import set_config_provider
from parsers.common_price.grouper import CommonPriceGrouper
from parsers.common_price.output import WriteDriverFactory, XlsWriterFactory
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xlsx_driver import XlsxWriterDriver
from services.configure import configure_services, ensure_services_configured
from services.doubles_service import DoublesService
from services.four_tochki_service import FourTochkiService
from services.help_service import HelpService
from services.mail_service import MailService
from services.mim_service import MimService
from services.parse_orchestrator import GrouperFactory, ParseOrchestrator, ParserFactory
from services.price_report import PriceReportService
from services.price_schema_service import PriceSchemaService
from services.service_provider import ServiceProvider
from services.vendor_activation import VendorActivationService
from services.vendor_parser import parser_for_vendor
from services.zapaska_service import ZapaskaService


def test_configure_registers_factories() -> None:
    """configure_services регистрирует все фабрики приложения."""
    ServiceProvider.clear()
    configure_services()
    assert ServiceProvider.is_configured()
    assert ServiceProvider.resolve(ParserFactory) is parser_for_vendor
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
    assert isinstance(ServiceProvider.resolve(PriceSchemaService), PriceSchemaService)
    assert isinstance(ServiceProvider.resolve(ZapaskaService), ZapaskaService)
    assert isinstance(ServiceProvider.resolve(FourTochkiService), FourTochkiService)
    assert isinstance(ServiceProvider.resolve(MimService), MimService)
    assert isinstance(ServiceProvider.resolve(MailService), MailService)
    assert isinstance(ServiceProvider.resolve(HelpService), HelpService)
    assert isinstance(ServiceProvider.resolve(VendorActivationService), VendorActivationService)


def test_configure_is_idempotent() -> None:
    """повторный configure_services не ломает регистрацию."""
    ServiceProvider.clear()
    configure_services()
    configure_services()
    assert ServiceProvider.resolve(ParserFactory) is parser_for_vendor
    assert ServiceProvider.resolve(GrouperFactory) is CommonPriceGrouper
    assert isinstance(ServiceProvider.resolve(ParseOrchestrator), ParseOrchestrator)


def test_resolved_services_share_factory_instances() -> None:
    """singleton-сервисы разрешаются одним экземпляром."""
    ServiceProvider.clear()
    configure_services()
    assert ServiceProvider.resolve(ParseOrchestrator) is ServiceProvider.resolve(ParseOrchestrator)


def test_composition_connects_service_graph() -> None:
    """Оркестратор, writer и отчёт о дублях используют зарегистрированный граф."""
    ServiceProvider.clear()
    configure_services()
    orchestrator = ServiceProvider.resolve(ParseOrchestrator)
    report = ServiceProvider.resolve(PriceReportService)
    doubles = ServiceProvider.resolve(DoublesService)

    writer = report._writer_factory([])

    assert orchestrator._parser_factory is ServiceProvider.resolve(ParserFactory)
    assert orchestrator._grouper_factory is ServiceProvider.resolve(GrouperFactory)
    assert writer.xls_writer is ServiceProvider.resolve(XlsWriterFactory)
    assert writer.write_driver is ServiceProvider.resolve(WriteDriverFactory)
    assert doubles._orchestrator is orchestrator
    assert doubles._report_service is report


def test_singleton_orchestrator_uses_current_config_provider() -> None:
    """Подмена ConfigProvider после resolve влияет на следующий разбор."""
    ServiceProvider.clear()
    configure_services()
    orchestrator = ServiceProvider.resolve(ParseOrchestrator)
    provider = MagicMock()
    set_config_provider(provider)
    entry = (MagicMock(), None)

    with (
        patch('services.vendor_source.vendor_entry_for', return_value=entry) as entry_for,
        patch('services.vendor_source.load_aliases_map', return_value={}),
        patch('services.vendor_source.load_reference_priority', return_value={}),
        patch.object(ParseOrchestrator, '_parse_supplier'),
    ):
        orchestrator.parse_vendor('poshk')

    entry_for.assert_called_once_with('poshk', provider)


def test_price_schema_service_uses_current_config_provider() -> None:
    """Подмена ConfigProvider после resolve влияет на следующую копию прайсов."""
    ServiceProvider.clear()
    configure_services()
    service = ServiceProvider.resolve(PriceSchemaService)
    provider = MagicMock()
    provider.price_folder.return_value = '/prices'
    provider.result_folder.return_value = '/prices/result'
    set_config_provider(provider)

    with patch('services.price_schema_service.backup_prices') as backup:
        assert service.snapshot()

    assert backup.call_args.args[0].as_posix() == '/prices'


def test_writer_factories_resolved_at_report_service_creation() -> None:
    """Writer-фабрики фиксируются при сборке, а ConfigProvider остаётся динамическим."""
    ServiceProvider.clear()
    configure_services()
    writer = MagicMock()
    report = ServiceProvider.resolve(PriceReportService)
    provider = MagicMock()
    set_config_provider(provider)
    ServiceProvider.register(XlsWriterFactory, MagicMock)
    ServiceProvider.register(WriteDriverFactory, MagicMock)

    with patch('services.price_report.CommonPriceOut', return_value=writer) as output:
        report.write_doubles([])

    assert output.call_args.kwargs['xls_writer'] is XlsWriter
    assert output.call_args.kwargs['write_driver'] is XlsxWriterDriver
    assert output.call_args.kwargs['config_provider'] is provider


def test_price_schema_service_is_singleton_for_nested_guards() -> None:
    """Вложенные guard работают на одном экземпляре с общей глубиной."""
    ServiceProvider.clear()
    configure_services()
    assert ServiceProvider.resolve(PriceSchemaService) is ServiceProvider.resolve(PriceSchemaService)


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
    assert ServiceProvider.resolve(ParserFactory) is parser_for_vendor
