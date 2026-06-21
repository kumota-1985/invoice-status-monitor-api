import ipaddress
import socket
from urllib.parse import urlparse


def assert_safe_external_url(url: str) -> None:
    """SSRF guard for user-supplied webhook URLs.

    Raises ValueError unless the URL is http(s) AND every address its host resolves to
    is a public address (blocks localhost, private, loopback, link-local, reserved,
    multicast and cloud-metadata endpoints).
    """
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError("could not parse URL")

    if parsed.scheme not in ("http", "https"):
        raise ValueError("must be an http or https URL")

    host = parsed.hostname
    if not host:
        raise ValueError("must include a host")
    if host.lower() in ("localhost", "metadata.google.internal") or host.lower().endswith(".localhost"):
        raise ValueError("host is not allowed")

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        infos = socket.getaddrinfo(host, port)
    except Exception:
        raise ValueError("host could not be resolved")

    for info in infos:
        addr = info[4][0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            raise ValueError("host resolved to an invalid address")
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            raise ValueError("host resolves to a non-public address")
