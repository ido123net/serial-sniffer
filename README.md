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
