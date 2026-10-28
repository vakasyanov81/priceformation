"""Подключение к IMAP: SSL и запасное разрешение имени через DNS-over-HTTPS.

Системный DNS в некоторых окружениях не отдаёт хост почтового сервера; тогда
адрес берётся у DNS-over-HTTPS, а сертификат всё равно проверяется по имени
хоста (SNI = host).
"""

from __future__ import annotations

import imaplib
import json
import logging
import socket
import ssl
import urllib.request

from domain.mail import MailConnectionError

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 30
_DOH_TIMEOUT_SECONDS = 10
_DOH_URLS = (
    'https://cloudflare-dns.com/dns-query?name={host}&type=A',
    'https://dns.google/resolve?name={host}&type=A',
)


def open_client(host: str, port: int) -> imaplib.IMAP4_SSL:
    """Подключиться к серверу; при сбое системного DNS — по адресам из DoH."""
    context = ssl.create_default_context()
    try:
        return imaplib.IMAP4_SSL(host, port, ssl_context=context, timeout=_TIMEOUT_SECONDS)
    except socket.gaierror:
        logger.warning(f'Системный DNS не разрешил {host!r}; пробую через DoH.')
    return _open_client_via_doh(host, port, context)


class _ImapSslByAddress(imaplib.IMAP4_SSL):
    """IMAP4_SSL, подключающийся к заранее разрешённому адресу.

    Нужен, когда системный DNS не отдаёт хост: адрес берётся из DoH,
    а сертификат всё равно проверяется по имени хоста (SNI = self.host).
    """

    def __init__(
        self,
        host: str,
        port: int,
        address: str,
        ssl_context: ssl.SSLContext,
        timeout: float,
    ) -> None:
        """Запомнить адрес для _create_socket и поднять базовый IMAP4_SSL."""
        self._address = address
        self._ssl_context = ssl_context
        super().__init__(host, port, ssl_context=ssl_context, timeout=timeout)

    def _create_socket(self, timeout: float | None) -> ssl.SSLSocket:
        if timeout is not None and not timeout:
            raise ValueError('Non-blocking socket (timeout=0) is not supported')
        raw = socket.create_connection((self._address, self.port), timeout)
        wrapped: ssl.SSLSocket = self._ssl_context.wrap_socket(raw, server_hostname=self.host)
        return wrapped


def _open_client_via_doh(host: str, port: int, context: ssl.SSLContext) -> imaplib.IMAP4_SSL:
    addresses = _doh_addresses(host)
    if not addresses:
        raise MailConnectionError(f'Не удалось разрешить {host!r} ни системным DNS, ни через DoH.')
    errors: list[str] = []
    for address in addresses:
        try:
            return _ImapSslByAddress(host, port, address, context, _TIMEOUT_SECONDS)
        except (OSError, ssl.SSLError) as exc:
            errors.append(f'{address}: {exc!r}')
    target = f'{host}:{port}'
    detail = '; '.join(errors)
    raise MailConnectionError(f'Не удалось подключиться к {target} ({detail})')


def _doh_addresses(host: str) -> list[str]:
    """IPv4-адреса хоста через DNS-over-HTTPS (Cloudflare, затем Google)."""
    for template in _DOH_URLS:
        request = urllib.request.Request(  # noqa: S310
            template.format(host=host),
            headers={'Accept': 'application/dns-json'},
        )
        try:
            with urllib.request.urlopen(request, timeout=_DOH_TIMEOUT_SECONDS) as response:  # noqa: S310  # nosec B310
                payload = json.load(response)
        except (OSError, ValueError) as exc:
            _log_doh_failure(template, host, exc)
            continue
        addresses = _doh_answers(payload)
        if addresses:
            return addresses
    return []


def _log_doh_failure(template: str, host: str, exc: Exception) -> None:
    """Записать сбой одного DoH-провайдера: без лога причина пустого результата теряется."""
    endpoint = template.split('?', maxsplit=1)[0]
    logger.warning(f'DoH {endpoint}, хост {host!r}: {exc!r}')


def _doh_answers(payload: object) -> list[str]:
    """IPv4-адреса из ответа DoH-JSON."""
    answers = payload.get('Answer', []) if isinstance(payload, dict) else []
    found: list[str] = []
    for answer in answers:
        address = _ipv4_of(answer)
        if address is not None:
            found.append(address)
    return found


def _ipv4_of(answer: object) -> str | None:
    """Строковый IPv4-адрес из записи ответа DoH, если запись — адрес."""
    if not isinstance(answer, dict) or answer.get('type') != 1:
        return None
    address = answer.get('data')
    return address if isinstance(address, str) else None
