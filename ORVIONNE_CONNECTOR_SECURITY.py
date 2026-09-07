import ipaddress
import re
import socket
from urllib.parse import urlparse

READ_ONLY_HTTP_METHODS = {"GET", "HEAD"}
BLOCKED_HOSTS = {"localhost", "metadata.google.internal"}
METADATA_IPS = {
    ipaddress.ip_network("169.254.169.254/32"),
    ipaddress.ip_network("169.254.0.0/16"),
}
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    *METADATA_IPS,
]
SECRET_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9_]{20,}\.[A-Za-z0-9_.-]{20,}\.[A-Za-z0-9_.-]{20,}\b"),
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*[^\s]{8,}"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
]


class ConnectorSecurityError(ValueError):
    pass


def require_resource_selection(config: dict, key: str) -> list[str]:
    values = config.get(key) or []
    if not isinstance(values, list) or not values:
        raise ConnectorSecurityError(f"{key} selection is required.")
    return [str(value) for value in values]


def validate_read_only_method(method: str) -> str:
    normalized = method.strip().upper()
    if normalized not in READ_ONLY_HTTP_METHODS:
        raise ConnectorSecurityError("Only GET and HEAD are allowed.")
    return normalized


def validate_internal_api_url(
    url: str,
    *,
    allowed_hosts: list[str] | None = None,
    allow_private_networks: bool = False,
) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ConnectorSecurityError("Internal API connector requires HTTPS URLs.")
    if not parsed.hostname:
        raise ConnectorSecurityError("URL hostname is required.")
    hostname = parsed.hostname.lower()
    if hostname in BLOCKED_HOSTS:
        raise ConnectorSecurityError("Blocked host is not allowed.")
    if allowed_hosts and hostname not in {host.lower() for host in allowed_hosts}:
        raise ConnectorSecurityError("Hostname is not in the connector allowlist.")
    validate_hostname_addresses(hostname, allow_private_networks=allow_private_networks)
    return url


def validate_hostname_addresses(hostname: str, *, allow_private_networks: bool = False) -> None:
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(hostname, None)}
    except socket.gaierror as exc:
        raise ConnectorSecurityError("Hostname could not be resolved.") from exc

    for address in addresses:
        ip = ipaddress.ip_address(address)
        if any(ip in network for network in METADATA_IPS):
            raise ConnectorSecurityError("Metadata service addresses are blocked.")
        if not allow_private_networks and any(ip in network for network in BLOCKED_NETWORKS):
            raise ConnectorSecurityError("Private or loopback addresses are blocked.")


def contains_secret_like_content(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def safe_text_for_indexing(text: str, max_size: int = 1_000_000) -> str:
    if len(text.encode("utf-8")) > max_size:
        raise ConnectorSecurityError("Content exceeds maximum indexing size.")
    if contains_secret_like_content(text):
        raise ConnectorSecurityError("Secret-like content detected.")
    return text.replace("\x00", "")
