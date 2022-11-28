from __future__ import annotations

import argparse
import contextlib
import logging
import os
import pathlib
import re
import signal
import sys
from datetime import datetime

from serial import PosixPollSerial

logger = logging.getLogger(__name__)

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|[\x00-\x09\x0B-\x1F]|[\x7f-\xA0]")


class GracefulExit(SystemExit):
    pass


def signal_handler(signum, frame):
    raise GracefulExit(1)


def delete_ansi_esc(text: bytes | str):
    if isinstance(text, bytes):
        text = text.decode(encoding="ISO-8859-1")
    return ANSI_ESCAPE.sub("", text)


@contextlib.contextmanager
def lock_dev(port: pathlib.Path):
    port_links = [link for link in os.listdir(port.parent) if os.path.samefile(port.parent / link, port)]
    try:
        for link in port_links:
            des = os.open(f"/var/lock/LCK..{link}", flags=(os.O_WRONLY | os.O_CREAT | os.O_TRUNC), mode=0o644)
            with open(des, "w") as f:
                f.write(f"{os.getpid()}\n")
        yield
    finally:
        for link in port_links:
            os.unlink(f"/var/lock/LCK..{link}")


def sniff_port(
    port: pathlib.Path | str,
    output: pathlib.Path | str | None = None,
    delete_esc_chars: bool = True,
    add_timestamp: bool = True,
) -> int:
    port = pathlib.Path(port)
    if output is not None:
        output = pathlib.Path(output)
    with lock_dev(port):
        return _sniff(port, output, delete_esc_chars, add_timestamp)


def _sniff(
    port: pathlib.Path,
    output: pathlib.Path | None = None,
    delete_esc_chars: bool = True,
    add_timestamp: bool = True,
) -> int:
    signal.signal(signal.SIGTERM, signal_handler)
    logger.info(f"Start sniffing port: {port}")
    serial = PosixPollSerial(
        port=str(port),
        baudrate=115200,
        timeout=30,
    )
    if output is not None:
        os.makedirs(output.parent, exist_ok=True)
        output = open(output, "w")
    else:
        output = sys.stdout
    with output as output_file:
        try:
            read_lines(delete_esc_chars, serial, output_file, add_timestamp)
        except (KeyboardInterrupt, GracefulExit):
            logger.info(f"Done sniffing port: {port}")
            return 0


def read_lines(delete_esc_chars, serial, output_file, add_timestamp):
    while True:
        line = serial.readline()
        if delete_esc_chars:
            line = delete_ansi_esc(line)
        else:
            line = line.decode()
        if add_timestamp:
            line = f"{str(datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))} {line}"
        output_file.write(line)
        output_file.flush()


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(prog="serial-sniffer")
    parser.add_argument(
        "-p",
        "--port",
        required=True,
        metavar="DEV_PORT",
        help="Dev port to sniff for exeample: `/dev/ttyUSB1`",
        type=pathlib.Path,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default=None,
        metavar="PATH",
        help="Output file (default: standard output)",
    )
    parser.add_argument(
        "--delete-esc-chars",
        action="store_true",
        help="Filename for serial output",
    )
    parser.add_argument(
        "--add-timestamp",
        action="store_true",
        help="Add timestamp to each line",
    )
    args = parser.parse_args()
    sniff_port(args.port, args.output, args.delete_esc_chars, args.add_timestamp)


if __name__ == "__main__":
    raise SystemExit(main())
