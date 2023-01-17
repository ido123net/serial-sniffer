from __future__ import annotations

import contextlib
import datetime
import logging
import os
import pathlib
import re
from typing import Generator

import psutil

logger = logging.getLogger(__name__)


LCK = "/var/lock/LCK..{}"


class PortInUse(Exception):
    pass


def filter_ansi_escape(line: str) -> str:
    ESC_CHARS_RE = r"(\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|[\x00-\x09]|\x0D)"
    ansi_escape = re.compile(ESC_CHARS_RE)
    return ansi_escape.sub("", line)


def add_line_timestamp(line: str) -> str:
    def timestamp() -> str:
        return datetime.datetime.now().strftime("[%H:%M:%S.%f]")

    return f"{timestamp()} {line}"


@contextlib.contextmanager
def lock_dev(port: pathlib.Path) -> Generator[None, None, None]:
    port_links = get_all_dir_links(port)
    logger.debug(f"{port_links = }")
    if in_use(port_links):
        raise PortInUse(f"Cannot lock {port}.")
    try:
        lock_ports(port_links)
        yield
    finally:
        release_ports(port_links)


def release_ports(port_links: list[str]) -> None:
    for port_link in port_links:
        logger.info(f"relesing port / port-link: {port_link}")
        os.unlink(LCK.format(port_link))


def lock_ports(port_links: list[str]) -> None:
    for port_link in port_links:
        lock_port(port_link)


def lock_port(port_link: str) -> None:
    logger.info(f"locking port: {port_link}")
    with open(LCK.format(port_link), "w") as f:
        f.write(f"   {os.getpid()}\n")


def in_use(port_links: list[str]) -> bool:
    pids = get_pids_using_port(port_links)
    if pids:
        return any(psutil.pid_exists(pid) for pid in pids)
    return False


def get_pids_using_port(port_links: list[str]) -> set[int]:
    pids = set()
    for port_link in port_links:
        try:
            with open(f"/var/lock/LCK..{port_link}") as f:
                pid = f.readline().strip()
                pids.add(int(pid))
        except FileNotFoundError:
            continue
    return pids


def get_all_dir_links(file_path: pathlib.Path) -> list[str]:
    return [
        link
        for link in os.listdir(file_path.parent)
        if os.path.samefile(file_path.parent / link, file_path)
    ]
