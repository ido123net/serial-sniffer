[![build status](https://github.com/ido123net/serial-sniffer/actions/workflows/main.yml/badge.svg)](https://github.com/ido123net/serial-sniffer/actions/workflows/main.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ido123net/serial-sniffer/main.svg)](https://results.pre-commit.ci/latest/github/ido123net/serial-sniffer/main)

# Serial Sniffer

## Installation

```shell
pip install serial-sniffer
```

## Usage

```shell
serial-sniffer  [-b <baudrate>] [--no-timestamp] [--raw] [-o <filename>] <PORT>
```
required parameters:
- `PORT` Is the port you want to sniff - this parameter is required

optional parameters:
- `-b <baudrate>` baudrate for the port.
  - default - 115200
- `-o <filename>` output to a file, `<filename>` is the path of the output file.
  - default - `sys.stdout`.
- `--raw` flag for raw output.
  - default - remove ascii ESC chars and some control ascii chars, also removing carriage return (`\r`).
- `--no-timestamp` flag to prevent adding timestamp for each line.
