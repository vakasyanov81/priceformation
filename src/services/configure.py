"""Сборка графа зависимостей приложения в ServiceProvider."""

from domain.config_context import get_config_provider
from parsers.common_price.grouper import CommonPriceGrouper
from parsers.common_price.output import WriteDriverFactory, XlsWriterFactory
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xlsx_driver import XlsxWriterDriver
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
from services.vendor_source import VendorSource
from services.zapaska_service import ZapaskaService


def configure_services() -> None:
    """Зарегистрировать фабрики и сервисы приложения. Повторный вызов безопасен."""
    _register_factories()
    _register_services()
    _register_update_services()


def _register_factories() -> None:
    """Фабрики парсеров, группировщика и писателей."""
    ServiceProvider.register(ParserFactory, lambda: parser_for_vendor)
    ServiceProvider.register(GrouperFactory, lambda: CommonPriceGrouper)
    ServiceProvider.register(XlsWriterFactory, lambda: XlsWriter)
    ServiceProvider.register(WriteDriverFactory, lambda: XlsxWriterDriver)


def _register_services() -> None:
    """Сервисы оркестрации: разбор, отчёты, запаска, форточки, активация поставщиков."""
    ServiceProvider.register(
        ParseOrchestrator,
        lambda: ParseOrchestrator(
            parser_factory=ServiceProvider.resolve(ParserFactory),
            grouper_factory=ServiceProvider.resolve(GrouperFactory),
            vendor_source=VendorSource(),
        ),
    )
    ServiceProvider.register(PriceReportService, _price_report_service)
    ServiceProvider.register(
        DoublesService,
        lambda: DoublesService(
            orchestrator=ServiceProvider.resolve(ParseOrchestrator),
            report_service=ServiceProvider.resolve(PriceReportService),
        ),
    )
    ServiceProvider.register(HelpService, HelpService)
    ServiceProvider.register(VendorActivationService, VendorActivationService)


def _price_report_service() -> PriceReportService:
    """Собрать writer-фабрики при создании сервиса, пути окружения читать при записи."""
    return PriceReportService.from_factories(
        xls_writer=ServiceProvider.resolve(XlsWriterFactory),
        write_driver=ServiceProvider.resolve(WriteDriverFactory),
        config_provider=get_config_provider,
    )


def _register_update_services() -> None:
    """Источники обновления прайсов (запаска, Форточки, МИМ, почта) и контроль схем прайсов."""
    ServiceProvider.register(ZapaskaService, ZapaskaService)
    ServiceProvider.register(FourTochkiService, FourTochkiService)
    ServiceProvider.register(MimService, MimService)
    ServiceProvider.register(MailService, MailService)
    ServiceProvider.register(PriceSchemaService, PriceSchemaService)


def ensure_services_configured() -> None:
    """Собрать граф, если контейнер ещё пуст (прямой вызов machine_json)."""
    if not ServiceProvider.is_configured():
        configure_services()
