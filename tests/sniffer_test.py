from __future__ import annotations

import sys

import pytest
import serial
import serial_sniffer.sniffer
from serial_sniffer.sniffer import Sniffer


def test_sniff_for(ser):
    sniffer = Sniffer(ser)
    print(sniffer.sniff_for(3))


def test_sniffer_lock_ports(monkeypatch, port, patch_Serial):
    monkeypatch.setattr(
        serial_sniffer.sniffer,
        "get_all_dir_links",
        lambda file_path: ["TEST", "EQ5_PBCM_0001"],
    )
    ser = serial.Serial(str(port))
    Sniffer(ser, lock_ports=True)


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
    ser,
    port,
    patch_datetime_now,
    kwargs,
    expected_output,
):
    sniffer = Sniffer(ser, stdout=sys.stdout, **kwargs)

    def my_reader(*args):
        yield b"\x1b[31m\x00Test Line - sniff_port\x1b[0m\r\n"

    monkeypatch.setattr(serial_sniffer.sniffer, "reader", my_reader)
    sniffer._sniff()
    out, _ = capfd.readouterr()
    assert out == expected_output
