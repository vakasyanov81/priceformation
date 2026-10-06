"""Тесты интеграции стратегий в BaseParser (демонстрация этапа 2)."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.strategies_integration import StrategiesIntegration
from parsers.vendor_config.models import VendorConfig


class TestStrategiesIntegration:
    """Демонстрация интеграции стратегий с BaseParser."""

    def test_integration_with_poshk_behavior(self) -> None:
        """Интеграция с поведением Пошка: normalize_size_chunks + title_keywords + map_on_opt."""
        config = VendorConfig.from_dict(
            {
                'enabled': 1,
                'code': 'poshk',
                'name': 'Пошк',
                'start_row': 14,
                'file_templates': ['price*.xls'],
                'sections': [
                    {
                        'id': '1',
                        'name': 'Пошк',
                        'columns': {
                            '0': 'code',
                            '1': 'title',
                            '2': 'price_opt',
                            '3': 'rest_count',
                        },
                        'category': {
                            'strategy': 'title_keywords',
                            'map': {
                                'ободная лента': 'Ободная лента',
                                'шина': 'Автошина',
                                'покрышка': 'Автошина',
                                'камера': 'Автокамера',
                                'диск': 'Диск',
                            },
                            'default': 'Разное',
                        },
                        'title': {'strategy': 'normalize_size_chunks'},
                        'pricing': {'policy': 'map_on_opt'},
                    }
                ],
            },
            'poshk',
            'poshk.json',
        )
        section = config.sections[0]
        integration = StrategiesIntegration(section, config.behavior)

        # Тест normalize_size_chunks
        row = RowItem({'title': '385/65 R22.5 ...'})
        prepared = integration.get_prepared_title(row)
        assert prepared == '385/65R22.5 ...'

        # Тест title_keywords category
        row = RowItem({'title': 'Шина Nortec'})
        category = integration.category_for(row)
        assert category == 'Автошина'

    def test_integration_with_pioner_behavior(self) -> None:
        """Интеграция с поведением Пионера: header_rows + manufacturer_from_category + minus_reserve."""
        config = VendorConfig.from_dict(
            {
                'enabled': 1,
                'code': 'pioner',
                'name': 'Пионер',
                'start_row': 12,
                'file_templates': ['price*.xls'],
                'behavior': {
                    'pipeline': ['category', 'min_rest', 'markup', 'title'],
                    'find_manufacturer_on_enrich': False,
                    'rest': 'minus_reserve',
                },
                'sections': [
                    {
                        'id': '3',
                        'name': 'Пионер',
                        'columns': {
                            '1': 'title',
                            '2': 'price_opt',
                            '4': 'rest_count',
                            '5': 'reserve_count',
                        },
                        'category': {
                            'strategy': 'header_rows',
                            'zero_rest_categories': ['прочие'],
                        },
                        'title': {'strategy': 'manufacturer_from_category', 'variant': ''},
                        'pricing': {'policy': 'map_on_opt'},
                    }
                ],
            },
            'pioner',
            'pioner.json',
        )
        section = config.sections[0]
        integration = StrategiesIntegration(section, config.behavior)

        # Тест header_rows (category из заголовков)
        row = RowItem({'title': 'автошины TRIANGLE'})
        category = integration.category_for(row)
        assert category == 'автошины'

        # Тест manufacturer_from_category
        row = RowItem({'title': 'Nortec ER-218', 'price_opt': 1000})
        # Заглушка manufacturer_reader возвращает None, поэтому title не изменится
        prepared = integration.get_prepared_title(row)
        assert prepared == 'Nortec ER-218'

        # Тест minus_reserve (остаток минус резерв)
        row = RowItem({'rest_count': 10, 'reserve_count': 3})
        rest = integration.get_item_rest(row)
        assert rest == 7

    def test_integration_with_mim_truck_behavior(self) -> None:
        """Интеграция с грузовыми Мим: percent_by_threshold."""
        config = VendorConfig.from_dict(
            {
                'enabled': 1,
                'code': 'mim',
                'name': 'Мим',
                'start_row': 2,
                'file_templates': ['price*.xls'],
                'sections': [
                    {
                        'id': 'mim_2',
                        'name': 'Мим грузовая',
                        'columns': {
                            '0': 'code',
                            '1': 'title',
                            '22': 'price_opt',
                        },
                        'category': {'strategy': 'fixed', 'value': 'Грузовая шина'},
                        'title': {'strategy': 'tire_compose', 'variant': 'mim_truck'},
                        'pricing': {
                            'policy': 'percent_by_threshold',
                            'rules': {'threshold': 13000, 'low': 0.07, 'high': 0.05},
                        },
                    }
                ],
            },
            'mim',
            'mim.json',
        )
        section = config.sections[0]
        integration = StrategiesIntegration(section, config.behavior)

        # Тест tire_compose(mim_truck)
        row = RowItem(
            {
                'width': '295',
                'height_percent': '75',
                'diameter': '22.5',
                'layering': '14',
                'intimacy': '2',
                'axis': '2',
            }
        )
        prepared = integration.get_prepared_title(row)
        assert prepared == '295/75R22.5 14 2 2'

        # Тест percent_by_threshold pricing (через strategy)
        # pricing не интегрирована в StrategiesIntegration, но стратегия создана
        assert section.pricing.policy == 'percent_by_threshold'

    def test_integration_with_zapaska_disk_behavior(self) -> None:
        """Интеграция с Запаской-диск: column_canonical + default title."""
        config = VendorConfig.from_dict(
            {
                'enabled': 1,
                'code': 'zapaska',
                'name': 'Запаска',
                'start_row': 2,
                'file_templates': ['price*.xls'],
                'sections': [
                    {
                        'id': '2',
                        'name': 'Запаска (диски)',
                        'columns': {
                            '0': 'code',
                            '1': 'title',
                            '2': 'price_opt',
                            '3': 'rest_count',
                        },
                        'category': {'strategy': 'column_canonical', 'unknown_skip': True},
                        'title': {'strategy': 'default'},
                        'pricing': {'policy': 'map_on_opt'},
                    }
                ],
            },
            'zapaska',
            'zapaska.json',
        )
        section = config.sections[0]
        integration = StrategiesIntegration(section, config.behavior)

        # Тест column_canonical category
        row = RowItem({'type_production': 'Диск'})
        category = integration.category_for(row)
        assert category == 'Диск'

        # Тест default title
        row = RowItem({'title': 'Replay HND'})
        prepared = integration.get_prepared_title(row)
        assert prepared == 'Replay HND'

    def test_integration_with_autosnab_behavior(self) -> None:
        """Интеграция с Автоснабом: fill_fields_from_title + identity pricing."""
        config = VendorConfig.from_dict(
            {
                'enabled': 1,
                'code': 'autosnab54',
                'name': 'Автоснаб',
                'start_row': 2,
                'file_templates': ['price*.xls'],
                'sections': [
                    {
                        'id': 'autosnab',
                        'name': 'Автоснаб',
                        'columns': {
                            '0': 'code',
                            '1': 'title',
                            '2': 'price_opt',
                            '3': 'rest_count',
                        },
                        'category': {'strategy': 'none'},
                        'title': {'strategy': 'fill_fields_from_title'},
                        'pricing': {'policy': 'identity'},
                    }
                ],
            },
            'autosnab54',
            'autosnab54.json',
        )
        section = config.sections[0]
        integration = StrategiesIntegration(section, config.behavior)

        # Тест fill_fields_from_title
        row = RowItem({'title': '205/55R16'})
        prepared = integration.get_prepared_title(row)
        assert prepared == '205/55R16'
        assert row.tire.width == '205'
        assert row.tire.height_percent == '55'
        assert row.tire.diameter == '16'

        # Тест identity pricing (через strategy)
        assert section.pricing.policy == 'identity'
