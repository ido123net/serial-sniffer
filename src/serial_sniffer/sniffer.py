from __future__ import annotations

import logging
import pathlib
import sys
import threading
import time
from io import StringIO
from threading import Event
from typing import TextIO

import serial

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
        event: Event | None = None,
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
        self.event = event

    def start_sniffing(self) -> threading.Thread:
        lock_ports(self.port_links)
        self.event = Event()
        assert isinstance(self.event, Event)
        self.thread = threading.Thread(
            target=self._sniff,
            daemon=True,
        )
        self.thread.start()
        return self.thread

    def stop_sniffing(self) -> None:
        assert isinstance(self.event, Event)
        assert isinstance(self.thread, threading.Thread)
        self.event.set()
        self.thread.join(timeout=5)
        release_ports(self.port_links)

    def sniff_for(self, secs: float) -> str:
        self.stdout = StringIO()
        self.start_sniffing()
        time.sleep(secs)
        self.stop_sniffing()
        return self.stdout.getvalue()

    def _sniff(self) -> None:
        while self.event is None or not self.event.is_set():
            line = self.serial.readline()
            line_decoded = line.decode("utf-8")
            if self.clean_line:  # pragma: no cover
                line_decoded = filter_ansi_escape(line_decoded)
            if self.add_timestamp:
                line_decoded = add_line_timestamp(line_decoded)
            if line:
                self.stdout.write(line_decoded)
                self.stdout.flush()
