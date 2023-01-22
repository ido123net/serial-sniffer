from __future__ import annotations

import multiprocessing
import sys

import pytest
import serial
import serial_sniffer.sniffer
from serial_sniffer.sniffer import Sniffer


def test_sniffer_init():
    ser = serial.Serial()
    sniffer = Sniffer(ser)
    sniffer.stop_sniffing()


def test_sniff_port():
    ser = serial.serial_for_url("loop://", timeout=1)
    ser.write(b"a\n")
    ser.write(b"b\n")
    ser.write(b"c\n")
    sniffer = Sniffer(ser, add_timestamp=False)
    with sniffer.sniff_port() as sniff:
        assert isinstance(sniff, multiprocessing.Process)


@pytest.mark.parametrize(
    ("kwargs", "expected_output"),
    (
        (
            {},
            "[17:05:55.123456] Test Line - sniff_port\n",
        ),
        (
            {
                "add_timestamp": False,
                "clean_line": False,
            },
            "\x1b[31m\x00Test Line - sniff_port\x1b[0m\r\n",
        ),
    ),
)
def test__sniff_port(
    monkeypatch,
    capfd,
    port,
    patch_datetime_now,
    kwargs,
    expected_output,
):
    ser = serial.serial_for_url("loop://", timeout=1)
    ser.write(b"a\n")
    ser.write(b"b\n")
    ser.write(b"c\n")
    sniffer = Sniffer(ser, stdout=sys.stdout, **kwargs)

    def my_reader(*args):
        yield b"\x1b[31m\x00Test Line - sniff_port\x1b[0m\r\n"

    monkeypatch.setattr(serial_sniffer.sniffer, "reader", my_reader)
    sniffer._sniff_port()
    out, _ = capfd.readouterr()
    assert out == expected_output
