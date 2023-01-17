from __future__ import annotations

from typing import Generator

import serial


def reader(serial: serial.Serial) -> Generator[bytes, None, None]:
    while True:
        yield serial.readline()
