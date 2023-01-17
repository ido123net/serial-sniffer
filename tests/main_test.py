from __future__ import annotations

import pytest
import serial

import serial_sniffer.main
from serial_sniffer.main import main


@pytest.fixture
def patch_Serial(monkeypatch):
    class TestSerial:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(serial, "Serial", TestSerial)


@pytest.fixture
def patch_Sniffer(monkeypatch):
    class TestSniffer:
        def __init__(*args, **kwargs):
            pass

        def sniff_port(self):
            return None

    monkeypatch.setattr(serial_sniffer.main, "Sniffer", TestSniffer)


def test_main(patch_Sniffer, patch_Serial):
    assert main(["/dev/TEST"]) is None
