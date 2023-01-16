import os
import pathlib
import subprocess
from serial_sniffer.utils import lock_dev

LCK_PATH = pathlib.Path("/var/lock/")

def test_lock_dev():
    port = pathlib.Path("/dev/EPM1")
    lock_file = LCK_PATH / f"LCK..{port.name}"
    with lock_dev(port):
        subprocess.call(["ls", str(LCK_PATH)])
    # os.unlink(lock_file)