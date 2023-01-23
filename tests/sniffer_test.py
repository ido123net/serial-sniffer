from __future__ import annotations

import sys

import serial

import serial_sniffer.sniffer
from serial_sniffer.sniffer import Sniffer


def test_sniff_for(ser):
    sniffer = Sniffer(ser, add_timestamp=False)
    assert sniffer.sniff_for(0.1) == "a\nb\nc\n"


def test_sniffer_lock_ports(monkeypatch, port, patch_Serial):
    monkeypatch.setattr(
        serial_sniffer.sniffer,
        "get_all_dir_links",
        lambda file_path: ["TEST", "EQ5_PBCM_0001"],
    )
    ser = serial.Serial(str(port))
    Sniffer(ser, lock_ports=True)


def test_sniff(
    ser,
    patch_datetime_now,
):
    sniffer = Sniffer(ser, stdout=sys.stdout)
    res = sniffer.sniff_for(0.1)
    exp = "[17:05:55.123456] a\n[17:05:55.123456] b\n[17:05:55.123456] c\n"
    assert res == exp
