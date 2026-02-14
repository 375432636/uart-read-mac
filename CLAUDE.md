# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cross-platform Python tool for monitoring USB UART/Serial connections and extracting device information (MAC addresses, domain/hostnames) from logs. Works on Windows, macOS, and Linux.

## Architecture

### Core Base Class (`uart_util.py`)

`UARTBase` provides cross-platform serial port operations:
- **Platform detection**: Automatically detects Windows/darwin/Linux and uses appropriate port prefixes (COM vs /dev/tty or /dev/cu)
- **Connection management**: `connect(port)` connects to specific port or waits for device if `port=None`
- **Auto-detection**: `wait_for_connection()` monitors for new USB UART devices by comparing port lists
- **Helper functions**: `list_uart_ports()`, `format_port_info()`, `get_platform()`

### Application Scripts

**`list_uart_devices.py`** - Utility to list all connected UART/Serial devices with detailed info (device path, manufacturer, product, VID/PID)

**`print_log.py`** - Log printer with session logging:
- Streams all UART output to stdout (original log lines)
- Saves logs to `static/%Y%m%d-%H%M%S.log` files
- Each UART connection creates a new session file
- Log files include millisecond timestamps: `[2025-02-14 15:30:45.123] log message`
- Session start/end times recorded in each file
- Handles device disconnection gracefully (returns, allowing reconnection)
- Uses `readline()` for line-by-line output

**`uart_mac_reader.py`** - Main tool for extracting device info:
- Searches for MAC addresses in `wifi:mode:sta (XX:XX:XX:XX:XX:XX)` format
- Searches for domain names (e.g., `lumin-vas-dev.deep-edge.cn`) using pattern `[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+){2,}`
- Determines environment: `env='dev'` if 'dev' in hostname (case-insensitive), else `env='main'`
- Output format: `WiFi MAC Address: XX:XX:XX:XX:XX:XX` and `→ host: xxx, env: xxx`
- Uses buffered reading (`serial_conn.read(in_waiting)`) to handle partial lines
- Filters out lines containing "Found AP" to reduce noise
- Auto-reconnects on device disconnect

## Running the Tools

### List available devices
```bash
python3 list_uart_devices.py
```

### Monitor and extract MAC addresses/domains (main tool)
```bash
# Auto-detect and wait for device
python3 uart_mac_reader.py

# Specify port
python3 uart_mac_reader.py -p /dev/ttyUSB0  # Linux/macOS
python3 uart_mac_reader.py -p COM3             # Windows

# Run once (no auto-reconnect)
python3 uart_mac_reader.py --once
```

### Simple log printing
```bash
python3 print_log.py [-p PORT] [--once]
```

## Platform-Specific Notes

**Linux**: User must be in 'dialout' or 'uucp' group: `sudo usermod -a -G dialout $USER`

**macOS**: May need drivers for USB-Serial adapters (FTDI, CH340, CP2102)

**Windows**: Uses COM ports, may need pywin32 for enhanced device detection

## Log Files

**`print_log.py` creates session-based logs in `static/` directory:**
- Filename format: `%Y%m%d-%H%M%S.log` (e.g., `20250214-153045.log`)
- Each connection = new session file
- Timestamps: `[YYYY-MM-DD HH:MM:SS.mmm]` format (millisecond precision)
- Session markers show start/end ISO timestamps
- Directory auto-created if missing
- Excluded from git via `.gitignore`

## Adding New Parsers

To add new log parsing patterns to `MACReader` or `UARTLogPrinter`:

1. Add regex pattern as class constant (e.g., `MAC_PATTERN`)
2. Create `parse_xxx(self, line)` method that returns parsed data or `None`
3. Call in `read_logs()` method within line processing loop
4. Print results with consistent indentation (`print(f"    Info: {data}")`)

## Error Handling Pattern

All tools handle disconnection gracefully:
- Catch `(serial.SerialException, OSError)` in inner loop
- Return normally (don't re-raise) to allow outer `run()` loop to handle reconnection
- The `run()` method wraps `read_logs()` in try/except and closes connection before continuing loop
