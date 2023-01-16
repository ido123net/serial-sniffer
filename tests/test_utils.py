import os
import pathlib
from serial_sniffer.utils import lock_dev

def test_lock_dev():
    port = pathlib.Path("/dev/FAKE")
    lock_file = f"/var/lock/LCK..{port.name}"
    with open(lock_file, "w") as f:
        f.write("0\n")
    # os.unlink(lock_file)