import socket
import logging

logger = logging.getLogger(__name__)

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None  # type: ignore
    PSUTIL_AVAILABLE = False


def is_network_available(
    host: str = "1.1.1.1", port: int = 53, timeout: float = 3.0
) -> bool:
    """Return True if we can reach the given host:port within ``timeout``."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def is_vpn_active() -> bool:
    """Return True if a VPN-like network interface is detected."""
    if not PSUTIL_AVAILABLE or psutil is None:
        logger.debug("psutil not available; cannot detect VPN interfaces.")
        return False
    try:
        interfaces = psutil.net_if_addrs()
        return any(
            name.startswith("tun") or name.startswith("ppp")
            for name in interfaces
        )
    except Exception as e:
        logger.debug("Unable to determine VPN status: %s", e)
        return False
