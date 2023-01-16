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
    ) -> None:
        self.serial = serial
        self.add_timestamp = add_timestamp
        self.clean_line = clean_line
        self.stdout = io.StringIO()

    def sniff_port(self):
        logger.info(f"[start] sniffing port - {serial.port}")
        try:
            self._sniff_port()
        finally:
            logger.info(f"[end] sniffing port - {serial.port}")

    def _sniff_port(self):
        for line in reader(serial):
            line = line.decode("latin-1")
            if self.clean_line:
                line = serial_sniffer.utils.filter_ansi_escape(line)
            if self.add_timestamp:
                line = serial_sniffer.utils.add_line_timestamp(line)
            self.stdout.write(line)
