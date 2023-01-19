from __future__ import annotations

import os
import pathlib
import tempfile

import psutil
import pytest

from serial_sniffer import utils


@pytest.fixture
def patch_pid_exits(monkeypatch):
    def my_pid_exists(pid):
        if pid == 1:
            return True

    monkeypatch.setattr(psutil, "pid_exists", my_pid_exists)


@pytest.fixture
def port_links(port):
    return utils.get_all_dir_links(port)


def test_get_all_dir_links():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)
        tmp_file = tmpdir_path / "tmp"
        with open(tmp_file, "w") as f:
            f.write("test\n")
        os.link(tmp_file, tmpdir_path / "tmp_link")
        assert set(utils.get_all_dir_links(tmp_file)) == {"tmp", "tmp_link"}


def test_lock_dev(monkeypatch, port):
    monkeypatch.setattr(
        utils,
        "in_use",
        lambda port_links: False,
    )
    with utils.lock_dev(port):
        for port_link in utils.get_all_dir_links(port):
            assert os.path.isfile(utils.LCK.format(port_link))
    assert not os.path.isfile(utils.LCK.format(port_link))


def test_port_in_use(monkeypatch, port):
    monkeypatch.setattr(
        utils,
        "in_use",
        lambda port_links: True,
    )
    with pytest.raises(utils.PortInUse):
        next(utils.lock_dev(port).gen)


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
    assert utils.filter_ansi_escape(line) == expected_output


def test_add_line_timestamp(patch_datetime_now):
    expected = "[17:05:55.123456] Test line\n"
    assert utils.add_line_timestamp("Test line\n") == expected


def test_lock_port(port):
    utils.lock_port(port.name)
    port_lck_filename = utils.LCK.format(port.name)
    assert os.path.isfile(port_lck_filename)
    with open(port_lck_filename) as f:
        data = f.read()
    assert data == f"   {os.getpid()}\n"
    os.unlink(port_lck_filename)


def test_get_pids_using_port(port_links):
    utils.lock_port(port_links[0])
    assert utils.get_pids_using_port(port_links) == {os.getpid()}


@pytest.mark.parametrize(("pids"), (([1]), ([1, 2])))
def test_in_use(patch_pid_exits, monkeypatch, port_links, pids):
    monkeypatch.setattr(
        utils,
        "get_pids_using_port",
        lambda port_links: pids,
    )
    assert utils.in_use(port_links)


@pytest.mark.parametrize(("pids"), (([]), ([2, 3])))
def test_not_in_use(patch_pid_exits, monkeypatch, port_links, pids):
    monkeypatch.setattr(
        utils,
        "get_pids_using_port",
        lambda port_links: pids,
    )
    assert not utils.in_use(port_links)
