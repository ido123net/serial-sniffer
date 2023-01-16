import contextlib
import datetime
import logging
import os
import pathlib
import re

logger = logging.getLogger(__name__)


def filter_ansi_escape(line: str):
    ESC_CHARS_RE = r"(\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|[\x00-\x09]|\x0D)"
    ansi_escape = re.compile(ESC_CHARS_RE)
    return ansi_escape.sub("", line)


def add_line_timestamp(
    line: str,
) -> str:
    def timestamp():
        return datetime.datetime.now().strftime("[%H:%M:%S.%f]")

    return f"{timestamp()} {line}"


@contextlib.contextmanager
def lock_dev(port: pathlib.Path):
    port_links = [link for link in os.listdir(port.parent) if os.path.samefile(port.parent / link, port)]
    for l in port_links:
        try:
            with open(f"/var/lock/LCK..{link}") as f:
                pid = f.readline()
        except Exception:
            raise
    in_use = any(os.path.exists(f"/var/lock/LCK..{link}") for link in port_links)
    assert not in_use, f"{port} is in use, check `/var/lock`"
    # TODO: check if the process still running
    try:
        for link in port_links:
            logger.info(f"locking port / port-link: {link}")
            des = os.open(f"/var/lock/LCK..{link}", flags=(os.O_WRONLY | os.O_CREAT | os.O_TRUNC), mode=0o644)
            with open(des, "w") as f:
                f.write(f"{os.getpid()}\n")
        yield
    finally:
        for link in port_links:
            logger.info(f"relesing port / port-link: {link}")
            os.unlink(f"/var/lock/LCK..{link}")
