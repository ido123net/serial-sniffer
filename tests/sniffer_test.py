from __future__ import annotations

import sys

import pytest
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


@pytest.mark.parametrize(
    ("kwargs", "expected_output"),
    (
        (
            {},
            "[17:05:55.123456] a\n[17:05:55.123456] b\n[17:05:55.123456] c\n",
        ),
    ),
)
def test_sniff(
    ser,
    patch_datetime_now,
    kwargs,
    expected_output,
):
    sniffer = Sniffer(ser, stdout=sys.stdout, **kwargs)
    assert sniffer.sniff_for(0.1) == expected_output
