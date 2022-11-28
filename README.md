# Serial Sniffer

## Installation

```shell
pip install serial-sniffer
```

## Usage

```shell
serial-sniffer -p/--dev-port DEV_PORT [-o/--output PATH] [--delete-esc-chars] [--add-timestamp]
```

- `DEV_PORT` Is the port you want to sniff - this parameter is required
- use `-o PATH` if you want to write the output to a file `PATH` is the path of the output file.
- use `--delete-esc-chars` if you want to delete escape characters from the output.
- use `--add-timestamp` to add timestamp for each line.
