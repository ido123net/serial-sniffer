from __future__ import annotations

import contextlib
import logging
import multiprocessing
import sys
from typing import Generator
from typing import TextIO

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
        stdout: TextIO = sys.stdout,
    ) -> None:
        self.serial = serial
        self.add_timestamp = add_timestamp
        self.clean_line = clean_line
        self.stdout = stdout
        self.process: multiprocessing.Process | None = None

    @contextlib.contextmanager
    def sniff_port(self) -> Generator[multiprocessing.Process, None, None]:
        logger.info(f"[start] sniffing port - {self.serial.port}")
        try:
            self.start_sniffing()
            assert isinstance(self.process, multiprocessing.Process)
            assert self.process.is_alive()
            yield self.process
        finally:
            self.stop_sniffing()
            logger.info(f"[end] sniffing port - {self.serial.port}")

    def start_sniffing(self) -> None:
        self.event = multiprocessing.Event()
        self.process = multiprocessing.Process(
            target=self._sniff_port,
            daemon=True,
            args=(self.event,),
        )
        self.process.start()

    def stop_sniffing(self) -> None:
        if self.process is not None:
            self.process.kill()

    def _sniff_port(self) -> None:
        for line in reader(self.serial):
            line_d = line.decode("latin-1")
            if self.clean_line:
                line_d = serial_sniffer.utils.filter_ansi_escape(line_d)
            if self.add_timestamp:
                line_d = serial_sniffer.utils.add_line_timestamp(line_d)
            self.stdout.write(line_d)
            self.stdout.flush()
