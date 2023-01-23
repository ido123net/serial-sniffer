from __future__ import annotations

import logging
import multiprocessing
import pathlib
import sys
import time
from io import StringIO
from multiprocessing.synchronize import Event
from typing import TextIO

import serial
from serial_sniffer.serial_reader import reader
from serial_sniffer.utils import add_line_timestamp
from serial_sniffer.utils import filter_ansi_escape
from serial_sniffer.utils import get_all_dir_links
from serial_sniffer.utils import lock_ports
from serial_sniffer.utils import release_ports

logger = logging.getLogger(__name__)


class Sniffer:
    def __init__(
        self,
        ser: serial.Serial,
        *,
        add_timestamp: bool = True,
        clean_line: bool = True,
        stdout: TextIO = sys.stdout,
        lock_ports: bool = False,
    ) -> None:
        self.serial = ser
        self.add_timestamp = add_timestamp
        self.clean_line = clean_line
        self.stdout = stdout
        if lock_ports:
            self.port_links = get_all_dir_links(pathlib.Path(ser.port))
        else:
            self.port_links = []

        # sniffer Process
        self.process: multiprocessing.Process | None = None
        self.event: Event | None = None

    def start_sniffing(self) -> multiprocessing.Process:
        if self.serial.exclusive is not True:
            self.serial.exclusive = True
        lock_ports(self.port_links)
        self.event = multiprocessing.Event()
        assert isinstance(self.event, Event)
        self.process = multiprocessing.Process(
            target=self._sniff,
            daemon=True,
        )
        self.process.start()
        return self.process

    def stop_sniffing(self) -> None:
        if isinstance(self.event, Event):
            self.event.set()
            assert isinstance(self.process, multiprocessing.Process)
            self.process.join(timeout=5)
            if self.process.is_alive():
                self.process.kill()
        release_ports(self.port_links)

    def sniff_for(self, secs: float) -> str:
        self.stdout = StringIO()
        self.start_sniffing()
        time.sleep(secs)
        self.stop_sniffing()
        print(self.stdout.tell())
        return self.stdout.getvalue()

    def _sniff(self) -> None:
        for line in reader(self.serial, self.event):
            line_d = line.decode("utf-8")
            if self.clean_line:
                line_d = filter_ansi_escape(line_d)
            if self.add_timestamp:
                line_d = add_line_timestamp(line_d)
            self.stdout.write(line_d)
            self.stdout.flush()
