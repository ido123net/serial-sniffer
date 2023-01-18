from __future__ import annotations

import io
import logging

import serial

import serial_sniffer.utils
from serial_sniffer.serial_reader import reader

logger = logging.getLogger(__name__)


class Sniffer:
    def __init__(
        self,
        serial: serial.Serial,
        *,
        add_timestamp: bool = True,
        clean_line: bool = True,
        stdout: io.StringIO | io.TextIOWrapper = io.StringIO(),
    ) -> None:
        self.serial = serial
        self.add_timestamp = add_timestamp
        self.clean_line = clean_line
        self.stdout = stdout

    def sniff_port(self) -> int:
        logger.info(f"[start] sniffing port - {serial.port}")
        try:
            self._sniff_port()
        finally:
            logger.info(f"[end] sniffing port - {serial.port}")
            return 0

    def _sniff_port(self) -> None:
        for line in reader(serial):
            line_d = line.decode("latin-1")
            if self.clean_line:
                line_d = serial_sniffer.utils.filter_ansi_escape(line_d)
            if self.add_timestamp:
                line_d = serial_sniffer.utils.add_line_timestamp(line_d)
            self.stdout.write(line_d)
