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
    except Exception:
        # ``socket.create_connection`` can raise a variety of exceptions
        # depending on the type and value of ``timeout`` or the reachability of
        # the host.  In addition to ``OSError`` (for network errors) it may
        # raise ``ValueError`` or ``TypeError`` when invalid parameters are
        # supplied.  Treat all of these cases as "network unavailable" instead
        # of propagating the error so callers get a simple True/False result.
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
