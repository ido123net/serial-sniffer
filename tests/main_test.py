from __future__ import annotations

import contextlib

import pytest
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


def test_main(patch_Sniffer, patch_Serial):
    assert main(["/dev/TEST"]) == 0
