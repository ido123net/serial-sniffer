from __future__ import annotations

import pytest
import serial

import serial_sniffer.serial_reader


@pytest.fixture
def patch_Serial(monkeypatch):
    class MySerial(serial.Serial):
        def readline(self, *args, **kwargs):
            return b"Test Line\n"

    monkeypatch.setattr(serial, "Serial", MySerial)


def test_reader(patch_Serial):
    ser = serial.Serial()
    assert next(serial_sniffer.serial_reader.reader(ser)) == b"Test Line\n"
