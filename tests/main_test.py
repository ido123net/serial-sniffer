from __future__ import annotations

import contextlib

import pytest
import serial
import serial_sniffer.main
from serial_sniffer.main import main


@pytest.fixture
def patch_Sniffer(monkeypatch):
    class TestProcess:
        def join(self):
            return

    class TestSniffer:
        def __init__(*args, **kwargs):
            pass

        @contextlib.contextmanager
        def sniff_port(self):
            try:
                yield TestProcess()
            finally:
                return

    monkeypatch.setattr(serial_sniffer.main, "Sniffer", TestSniffer)
    monkeypatch.setattr(
        serial, "Serial",
        lambda *args: serial.serial_for_url("loop://"),
    )


def test_main(patch_Sniffer):
    assert main(["/dev/TEST"]) == 0
