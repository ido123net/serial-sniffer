import contextlib
import datetime
import logging
import os
import pathlib
import re

logger = logging.getLogger(__name__)


class PortInUse(Exception):
    pass

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
    port_links = get_all_dir_links(port)
    pids = []
    for l in port_links:
        try:
            with open(f"/var/lock/LCK..{l}") as f:
                pid = f.readline().strip()
                pids.append(int(pid))
        except FileNotFoundError:
            continue
    for pid in pids:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise PortInUse(f"Cannot lock {port} process {pid} is using it.")
    try:
        for link in port_links:
            logger.info(f"locking port / port-link: {link}")
            des = os.open(f"/var/lock/LCK..{link}", flags=(os.O_WRONLY | os.O_CREAT | os.O_TRUNC), mode=0o644)
            with open(des, "w") as f:
                f.write(f"   {os.getpid()}\n")
        yield
    finally:
        for link in port_links:
            logger.info(f"relesing port / port-link: {link}")
            os.unlink(f"/var/lock/LCK..{link}")

def get_all_dir_links(file_path: pathlib.Path):
    return [link for link in os.listdir(file_path.parent) if os.path.samefile(file_path.parent / link, file_path)]
