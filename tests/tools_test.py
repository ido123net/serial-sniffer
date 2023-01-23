from __future__ import annotations

import os
import threading

from serial_sniffer.sniffer import Sniffer
from serial_sniffer.tools import sniff_many_ctx
from serial_sniffer.tools import sniff_one_ctx


def test_sniff_one_ctx(ser):
    sniffer = Sniffer(ser, add_timestamp=False, stdout=open(os.devnull, "w"))
    with sniff_one_ctx(sniffer) as sniff:
        assert isinstance(sniff, threading.Thread)


def test_sniff_many_ctx(ser):
    sniffer1 = Sniffer(ser, add_timestamp=False, stdout=open(os.devnull, "w"))
    sniffer2 = Sniffer(ser, add_timestamp=False, stdout=open(os.devnull, "w"))
    with sniff_many_ctx([sniffer1, sniffer2]) as sniffers:
        for sniffer in sniffers:
            assert isinstance(sniffer, threading.Thread)
