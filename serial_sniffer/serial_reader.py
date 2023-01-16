import signal

import serial

def reader(serial: serial.Serial):
    def _signal_handler(signum, frame):
        raise SystemExit(signum, frame)
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    while True:
        yield serial.readline()
