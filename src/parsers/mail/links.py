"""Ссылки на xlsx-прайсы в тексте письма.

Чистые функции над строками: без сети и файлового IO.
"""

import html
import re
from email.message import Message
from urllib.parse import unquote, urlsplit

from parsers.mail.body import message_text

_URL = re.compile(r'https?://[^\s"\'<>]+', re.IGNORECASE)
_TRAILING_PUNCTUATION = '.,;:)]}'


def xlsx_links(text: str) -> list[str]:
    """Уникальные ссылки на .xlsx из текста письма в порядке появления."""
    links: list[str] = []
    for match in _URL.finditer(html.unescape(text)):
        url = match.group(0).rstrip(_TRAILING_PUNCTUATION)
        if _is_xlsx(url) and url not in links:
            links.append(url)
    return links


def single_xlsx_link(message: Message) -> str | None:
    """Единственная ссылка на xlsx в теле письма; нет или несколько — None."""
    links = xlsx_links(message_text(message))
    return links[0] if len(links) == 1 else None


def url_filename(url: str) -> str:
    """Имя файла из последнего сегмента пути ссылки."""
    return unquote(urlsplit(url).path.rsplit('/', 1)[-1])


def _is_xlsx(url: str) -> bool:
    """Путь ссылки оканчивается на .xlsx (регистр не важен)."""
    return urlsplit(url).path.lower().endswith('.xlsx')
