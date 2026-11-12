"""Сборка выходных источников по реальным моделям пакетов до первой записи."""

from collections.abc import Mapping, Set
from functools import partial

from domain.battery.result import BatteryResult
from domain.product_group_result import ProductGroupResult, ProductPosition, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.protocols import ConfigProvider
from parsers.base_parser.nomenclature_correction import clear_nomenclature_cache, get_nomenclature_corrected_title
from parsers.battery.output import BatteryOutputSource
from parsers.common_price.tire_output import TireOutputSource
from parsers.data_provider.doubles_settings import load_doubles_settings
from parsers.writer.group_files import GroupFileWriter
from parsers.writer.jsonl_writer import jsonl_output_files
from parsers.writer.output_plan import GroupOutputSource, prepare_output_plan
from parsers.writer.templates.all_templates import all_writer_templates, get_writer_template, writer_templates_by_name
from parsers.writer.templates.group_output import TemplateOutput
from parsers.writer.templates.tmpl.for_batteries import ForBatteries
from parsers.writer.templates.tmpl.for_doubles import ForDoubles


def output_sources(
    packages: Mapping[ProductGroup, ProductGroupResult[ProductPosition]], config: ConfigProvider
) -> dict[ProductGroup, GroupOutputSource]:
    """Чужая модель пакета отклоняется до подготовки и записи файлов."""
    clear_nomenclature_cache()
    sources: dict[ProductGroup, GroupOutputSource] = {
        ProductGroup.TIRE_AND_DISK: TireOutputSource(TireAndDiskResult()),
        ProductGroup.BATTERIES: BatteryOutputSource(BatteryResult()),
    }
    for group, package in packages.items():
        if isinstance(package, BatteryResult):
            sources[group] = BatteryOutputSource(package)
        elif isinstance(package, TireAndDiskResult):
            settings = load_doubles_settings(tuple(writer_templates_by_name()), config)
            sources[group] = TireOutputSource(
                package, settings, partial(get_nomenclature_corrected_title, config_provider=config)
            )
        else:
            raise TypeError(f'Нет выходного преобразователя для {group.value}: {type(package).__name__}')
    return sources


def write_group_prices(
    writer: GroupFileWriter,
    sources: Mapping[ProductGroup, GroupOutputSource],
    *,
    template: str | None,
    as_jsonl: bool,
    selected: Set[ProductGroup],
) -> list[str]:
    """Проверить весь набор шаблонов, затем записать явно выбранные для них группы."""
    if template is None:
        outputs = _default_outputs(selected)
        selections = {output.template_id: _groups(output).intersection(selected) for output in outputs}
        paths = writer.write_plan(prepare_output_plan(outputs, sources, selections=selections), as_jsonl=as_jsonl)
    else:
        output = get_writer_template(template)().output_spec()
        paths = writer.write([output], sources, selected=selected, as_jsonl=as_jsonl)
    return jsonl_output_files(paths) if as_jsonl else paths


def _groups(output: TemplateOutput) -> set[ProductGroup]:
    return {group.id for group in output.groups}


def _default_outputs(selected: Set[ProductGroup]) -> list[TemplateOutput]:
    templates = [*all_writer_templates(), ForBatteries, ForDoubles]
    outputs = [template().output_spec() for template in templates]
    return [output for output in outputs if _groups(output).intersection(selected)]
