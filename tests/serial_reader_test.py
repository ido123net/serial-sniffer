from __future__ import annotations

import multiprocessing

import pytest
import serial
import serial_sniffer.serial_reader


def test_reader():
    ser = serial.serial_for_url("loop://", timeout=1)
    ser.write(b"a\n")
    ser.write(b"b\n")
    ser.write(b"c\n")
    event = multiprocessing.Event()
    reader = serial_sniffer.serial_reader.reader(ser, event)
    assert next(reader) == b"a\n"
    assert next(reader) == b"b\n"
    event.set()
    with pytest.raises(StopIteration):
        next(reader)
