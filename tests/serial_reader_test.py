from __future__ import annotations

import multiprocessing

import pytest
import serial

import serial_sniffer.serial_reader


def test_reader(patch_Serial):
    ser = serial.Serial()
    event = multiprocessing.Event()
    reader = serial_sniffer.serial_reader.reader(ser, event)
    line = next(reader)
    assert line == b"Test Line\n"
    event.set()
    with pytest.raises(StopIteration):
        next(reader)
    reader = serial_sniffer.serial_reader.reader(ser, event)
    with pytest.raises(StopIteration):
        next(reader)
