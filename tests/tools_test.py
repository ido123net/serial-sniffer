from __future__ import annotations

import multiprocessing

from serial_sniffer.sniffer import Sniffer
from serial_sniffer.tools import sniff_one_ctx


def test_sniff_one_ctx(ser):
    sniffer = Sniffer(ser, add_timestamp=False)
    with sniff_one_ctx(sniffer) as sniff:
        assert isinstance(sniff, multiprocessing.Process)
