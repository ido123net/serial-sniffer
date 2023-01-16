from __future__ import annotations

import argparse
import logging
import pathlib
from typing import Sequence

import serial

from serial_sniffer.sniffer import sniff_port


def main(argv: Sequence[str] | None = None):
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] | %(name)s | %(process)d | %(message)s",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "port",
        help="Port to sniff",
        type=pathlib.Path,
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        type=int,
        help="The baudrate for the serials",
        default=115200,
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Do not add timestamp to each line",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Do not clean ESC chars from lines",
    )
    args = parser.parse_args(argv)
    ser = serial.Serial(args.port, args.baudrate)
    sniff_port(ser, add_timestamp=(not args.no_timestamp),
               clean_line=(not args.raw))


if __name__ == "__main__":
    raise SystemExit(main())
