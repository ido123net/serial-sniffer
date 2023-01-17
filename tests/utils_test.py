from __future__ import annotations

import datetime
import os
import pathlib
import tempfile

import psutil
import pytest

import serial_sniffer.utils
from serial_sniffer.utils import add_line_timestamp
from serial_sniffer.utils import filter_ansi_escape
from serial_sniffer.utils import get_all_dir_links
from serial_sniffer.utils import get_pids_using_port
from serial_sniffer.utils import in_use
from serial_sniffer.utils import LCK
from serial_sniffer.utils import lock_dev
from serial_sniffer.utils import lock_port
from serial_sniffer.utils import PortInUse


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class mydatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return datetime.datetime(2020, 12, 25, 17, 5, 55, 123456)

    monkeypatch.setattr(datetime, "datetime", mydatetime)


@pytest.fixture
def patch_pid_exits(monkeypatch):
    def my_pid_exists(pid):
        if pid == 1:
            return True

    monkeypatch.setattr(psutil, "pid_exists", my_pid_exists)


@pytest.fixture
def port(monkeypatch):
    monkeypatch.setattr(
        serial_sniffer.utils,
        "get_all_dir_links",
        lambda file_path: ["TEST", "EQ5_PBCM_0001"],
    )
    return pathlib.Path("/dev/TEST")


@pytest.fixture
def port_links(port):
    return get_all_dir_links(port)


def test_get_all_dir_links():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)
        tmp_file = tmpdir_path / "tmp"
        with open(tmp_file, "w") as f:
            f.write("test\n")
        os.link(tmp_file, tmpdir_path / "tmp_link")
        assert get_all_dir_links(tmp_file) == ["tmp", "tmp_link"]


def test_lock_dev(monkeypatch, port):
    monkeypatch.setattr(
        serial_sniffer.utils,
        "in_use",
        lambda port_links: False,
    )
    with lock_dev(port):
        for port_link in get_all_dir_links(port):
            assert os.path.isfile(LCK.format(port_link))
    assert not os.path.isfile(LCK.format(port_link))


def test_port_in_use(monkeypatch, port):
    monkeypatch.setattr(
        serial_sniffer.utils,
        "in_use",
        lambda port_links: True,
    )
    with pytest.raises(PortInUse):
        next(lock_dev(port).gen)


@pytest.mark.parametrize(
    ("line", "expected_output"),
    (
        ("\u001b[31mTest\n\u001b[0m", "Test\n"),
        ("Test\r\n", "Test\n"),
        ("\x00", ""),
        ("\x03", ""),
    ),
)
def test_filter_ansi_escape(line, expected_output):
    assert filter_ansi_escape(line) == expected_output


def test_add_line_timestamp(patch_datetime_now):
    assert add_line_timestamp("Test line\n") == "[17:05:55.123456] Test line\n"


def test_lock_port(port):
    lock_port(port.name)
    port_lck_filename = LCK.format(port.name)
    assert os.path.isfile(port_lck_filename)
    with open(port_lck_filename) as f:
        data = f.read()
    assert data == f"   {os.getpid()}\n"
    os.unlink(port_lck_filename)


def test_get_pids_using_port(port_links):
    lock_port(port_links[0])
    assert get_pids_using_port(port_links) == {os.getpid()}


@pytest.mark.parametrize(("pids"), (([1]), ([1, 2])))
def test_in_use(patch_pid_exits, monkeypatch, port_links, pids):
    monkeypatch.setattr(
        serial_sniffer.utils,
        "get_pids_using_port",
        lambda port_links: pids,
    )
    assert in_use(port_links)


@pytest.mark.parametrize(("pids"), (([]), ([2, 3])))
def test_not_in_use(patch_pid_exits, monkeypatch, port_links, pids):
    monkeypatch.setattr(
        serial_sniffer.utils,
        "get_pids_using_port",
        lambda port_links: pids,
    )
    assert not in_use(port_links)
