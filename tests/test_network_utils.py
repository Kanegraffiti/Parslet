import types

from parslet.utils import network_utils


class DummyConn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_is_network_available_true(monkeypatch):
    def fake_create_connection(addr, timeout=0):
        return DummyConn()

    monkeypatch.setattr(
        network_utils.socket, "create_connection", fake_create_connection
    )
    assert (
        network_utils.is_network_available("1.1.1.1", 53, timeout=0.1) is True
    )


def test_is_network_available_false(monkeypatch):
    def fake_create_connection(addr, timeout=0):
        raise OSError

    monkeypatch.setattr(
        network_utils.socket, "create_connection", fake_create_connection
    )
    assert (
        network_utils.is_network_available("1.1.1.1", 53, timeout=0.1) is False
    )


def test_is_vpn_active_true(monkeypatch):
    def fake_net_if_addrs():
        return {"tun0": []}

    monkeypatch.setattr(network_utils, "PSUTIL_AVAILABLE", True)
    monkeypatch.setattr(
        network_utils,
        "psutil",
        types.SimpleNamespace(net_if_addrs=fake_net_if_addrs),
    )
    assert network_utils.is_vpn_active() is True


def test_is_vpn_active_false(monkeypatch):
    def fake_net_if_addrs():
        return {"eth0": []}

    monkeypatch.setattr(network_utils, "PSUTIL_AVAILABLE", True)
    monkeypatch.setattr(
        network_utils,
        "psutil",
        types.SimpleNamespace(net_if_addrs=fake_net_if_addrs),
    )
    assert network_utils.is_vpn_active() is False
