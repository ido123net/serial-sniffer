from __future__ import annotations

import multiprocessing

import pytest
import serial_sniffer.serial_reader


def test_reader(ser):
    event = multiprocessing.Event()
    reader = serial_sniffer.serial_reader.reader(ser, event)
    assert next(reader) == b"a\n"
    assert next(reader) == b"b\n"
    event.set()
    with pytest.raises(StopIteration):
        next(reader)
