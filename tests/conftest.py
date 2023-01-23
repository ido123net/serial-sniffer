from __future__ import annotations

import datetime
import pathlib

import pytest
import serial
from serial_sniffer import utils


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class mydatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return datetime.datetime(2020, 12, 25, 17, 5, 55, 123456)

    monkeypatch.setattr(datetime, "datetime", mydatetime)


@pytest.fixture
def port(monkeypatch):
    monkeypatch.setattr(
        utils,
        "get_all_dir_links",
        lambda file_path: ["TEST", "EQ5_PBCM_0001"],
    )
    return pathlib.Path("/dev/TEST")


@pytest.fixture
def ser():
    ser = serial.serial_for_url("loop://", timeout=3)
    ser.write(b"a\n")
    ser.write(b"b\n")
    ser.write(b"c\n")
    return ser


@pytest.fixture
def patch_Serial(monkeypatch):
    class MySerial(serial.Serial):
        def open(self):
            return

    monkeypatch.setattr(serial, "Serial", MySerial)
