import os
import pathlib
import subprocess
import tempfile

import serial_sniffer.utils



def test_get_all_dir_links():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = pathlib.Path(tmpdir)
        tmp_file = tmpdir_path / "tmp"
        with open(tmp_file, "w") as f:
            f.write("test\n")
        os.link(tmp_file, tmpdir_path / "tmp_link")
        assert serial_sniffer.utils.get_all_dir_links(tmp_file) == ["tmp", "tmp_link"]

def test_lock_dev(monkeypatch):
    def mock_get_all_dir_links(file_path):
        return [
            "TEST",
            "EQ5_PBCM_0001",
        ]
    monkeypatch.setattr(serial_sniffer.utils, "get_all_dir_links", mock_get_all_dir_links)
    monkeypatch.setattr(serial_sniffer.utils, "in_use", lambda port_links:  False)
    port = pathlib.Path("/dev/TEST")
    port_links = serial_sniffer.utils.get_all_dir_links(port)
    with serial_sniffer.utils.lock_dev(port):
        for port_link in port_links:
            assert os.path.isfile(serial_sniffer.utils.LCK.format(port_link))
    assert not os.path.isfile(serial_sniffer.utils.LCK.format(port_link))
