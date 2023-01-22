from __future__ import annotations

import datetime
import pathlib

import pytest
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
