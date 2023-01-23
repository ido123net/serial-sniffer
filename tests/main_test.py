from __future__ import annotations

import pytest
import serial
import serial_sniffer.main
from serial_sniffer.main import main


@pytest.fixture
def patch_Sniffer(monkeypatch):
    class TestSniffer:
        def __init__(self, ser, *args, **kwargs):
            self.serial = ser

        def start_sniffing(self):
            return

        def stop_sniffing(self):
            return

    monkeypatch.setattr(serial_sniffer.main, "Sniffer", TestSniffer)
    monkeypatch.setattr(
        serial,
        "Serial",
        lambda *args: serial.serial_for_url("loop://"),
    )


def test_main(patch_Sniffer):
    assert main(["/dev/TEST"]) == 0
