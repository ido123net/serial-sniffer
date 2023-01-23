from __future__ import annotations

import contextlib
import logging
import threading
from typing import Generator

from serial_sniffer.sniffer import Sniffer

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def sniff_one_ctx(
    sniffer: Sniffer,
) -> Generator[threading.Thread, None, None]:
    logger.info(f"[start] sniffing port - {sniffer.serial.port}")
    try:
        yield sniffer.start_sniffing()
    finally:
        sniffer.stop_sniffing()
        logger.info(f"[end] sniffing port - {sniffer.serial.port}")


@contextlib.contextmanager
def sniff_many_ctx(
    sniffers: list[Sniffer],
) -> Generator[list[threading.Thread], None, None]:
    _ports = [sniffer.serial.port for sniffer in sniffers]
    logger.debug(f"[start] sniffing ports - {_ports}")
    try:
        yield [sniffer.start_sniffing() for sniffer in sniffers]
    finally:
        for sniffer in sniffers:
            sniffer.stop_sniffing()
        logger.debug(f"[end] sniffing ports - {_ports}")
