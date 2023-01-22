from __future__ import annotations

from multiprocessing.synchronize import Event
from typing import Generator

import serial


def reader(
    serial: serial.Serial,
    event: Event | None = None,
) -> Generator[bytes, None, None]:
    while event is None or not event.is_set():
        yield serial.readline()
    return
