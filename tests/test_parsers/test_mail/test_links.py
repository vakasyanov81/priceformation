"""Поиск ссылок на xlsx в тексте письма."""

import pytest

from parsers.mail.links import url_filename, xlsx_links


def test_xlsx_links_plain_text() -> None:
    """Ссылка на xlsx в тексте письма находится; хвостовая пунктуация отбрасывается."""
    assert xlsx_links('Прайс: https://4tochki.ru/files/ostatki.xlsx.') == ['https://4tochki.ru/files/ostatki.xlsx']


def test_xlsx_links_html_href_with_entities() -> None:
    """Ссылка из href с HTML-сущностями в query декодируется."""
    text = '<a href="https://x.ru/get.xlsx?a=1&amp;b=2">скачать</a>'
    assert xlsx_links(text) == ['https://x.ru/get.xlsx?a=1&b=2']


def test_xlsx_links_skips_other_files_and_dedupes() -> None:
    """Не-xlsx ссылки отбрасываются, повторы схлопываются."""
    text = 'https://x.ru/a.pdf https://x.ru/p.XLSX https://x.ru/p.XLSX'
    assert xlsx_links(text) == ['https://x.ru/p.XLSX']


def test_xlsx_links_none() -> None:
    """Без ссылок на xlsx список пуст."""
    assert xlsx_links('без ссылок') == []


@pytest.mark.parametrize(
    ('url', 'expected'),
    [
        ('https://x.ru/files/%D0%BF.xlsx?token=1', 'п.xlsx'),
        ('https://x.ru/ostatki.xlsx', 'ostatki.xlsx'),
        ('ostatki.xlsx', 'ostatki.xlsx'),
        ('https://x.ru', ''),
    ],
)
def test_url_filename(url: str, expected: str) -> None:
    """Имя файла берётся из пути без query и декодируется."""
    assert url_filename(url) == expected


_FOURTOCHKI_BODY = (
    'В приложении информация о наличии товара на складе Пауэр Интернэшнл-шины.\n'
    'Рассылка: склад Новосиб..\n'
    'Ссылка для скачивания: https://b2b.pwrs.ru/export_data/M32334.xlsx.\n'
    'Примечание: данное письмо высылается автоматически с сервера «Форточки», '
    'пожалуйста, не отвечайте на него.\n'
)


def test_xlsx_links_fourtochki_letter() -> None:
    """Письмо Форточек: ссылка находится без точки в конце, имя файла — M32334.xlsx."""
    links = xlsx_links(_FOURTOCHKI_BODY)
    assert links == ['https://b2b.pwrs.ru/export_data/M32334.xlsx']
    assert url_filename(links[0]) == 'M32334.xlsx'
