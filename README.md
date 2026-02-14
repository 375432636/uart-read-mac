# UART MAC Reader

Cross-platform Python tool for monitoring USB UART/Serial connections and extracting device information (MAC addresses, domain/hostnames) from logs. Works on Windows, macOS, and Linux.

## Features

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Auto-detection**: Automatically waits for USB UART device connection
- **MAC Address Extraction**: Extracts WiFi MAC addresses from `wifi:mode:sta (XX:XX:XX:XX:XX:XX)` format
- **Domain Parsing**: Detects server domains and determines environment (dev/main)
- **Session Logging**: Saves logs with millisecond timestamps
- **Auto-reconnect**: Automatically reconnects when device is disconnected

## Installation

### Install from GitHub

```bash
# Install latest version
pip install git+https://github.com/375432636/uart-read-mac.git

# Install specific version
pip install git+https://github.com/375432636/uart-read-mac.git@v1.0.0
```

### Platform Requirements

**Linux:**
```bash
# Add user to dialout group (required for USB serial access)
sudo usermod -a -G dialout $USER
# Then log out and log back in
```

**macOS:**
- May need to install drivers for USB-Serial adapters (FTDI, CH340, CP2102)

**Windows:**
- Uses COM ports, no additional setup required

## Usage

### List UART Devices

List all connected UART/Serial devices with detailed information:

```bash
list-uart
```

Output:
```
Platform: darwin
Found 1 UART device(s):

Device 1:
  Port:       /dev/ttyUSB0
  Name:       CP2102
  Description:  Silicon Labs CP2102
  Maker:       Silicon Labs
  Product:     CP2102
  Vendor ID:  10C4
  Product ID:  EA60
```

### Read MAC Addresses

Monitor UART and extract MAC addresses with domain information:

```bash
# Auto-detect and wait for device
uart-mac-reader

# Specify port
uart-mac-reader -p /dev/ttyUSB0

# Specify baud rate (default: 115200)
uart-mac-reader -p /dev/ttyUSB0 -b 9600

# Run once (no auto-reconnect)
uart-mac-reader --once
```

Output:
```
[*] Monitoring for MAC addresses (Ctrl+C to stop)...

WiFi MAC Address: AA:BB:CC:DD:EE:FF
    Log: wifi:mode:sta (aa:bb:cc:dd:ee:ff) connecting to https://lumin-vas-dev.deep-edge.cn
    → host: lumin-vas-dev.deep-edge.cn, env: dev
```

### Print Logs

Monitor and log UART output with session-based file saving:

```bash
# Auto-detect and wait for device
print-log

# Specify port
print-log -p /dev/ttyUSB0

# Run once (no auto-reconnect)
print-log --once
```

**Features:**
- Logs are saved to `static/YYYYMMDD-HHMMSS.log` files
- Each connection creates a new session file
- Log files include millisecond timestamps: `[2025-02-14 15:30:45.123] message`
- Session markers show start/end ISO timestamps

**Log file example:**
```
Session started: 2025-02-14T15:30:45.123456
============================================================
[2025-02-14 15:30:45.234] I (6099) AudioService: sample_rate=16000
[2025-02-14 15:30:46.123] I (7559) PowerManager: Battery: 70%
============================================================
Session ended: 2025-02-14T15:30:50.789012
```

## Command-line Options

All tools support these common options:

```bash
-p, --port    Serial port device (e.g., /dev/ttyUSB0, COM3)
              If not specified, waits for device connection
-b, --baudrate  Serial baud rate (default: 115200)
--once         Run once and exit (do not reconnect on disconnect)
```

## Domain/Environment Detection

The tool automatically detects environment from domain names:

- **dev**: If domain contains "dev" (case-insensitive)
- **main**: Otherwise

Example:
- `lumin-vas-dev.deep-edge.cn` → `env: dev`
- `lumin-vas.deep-edge.cn` → `env: main`

## Project Structure

```
uart-read-mac/
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── LICENSE                 # MIT License
├── uart_util.py            # Core utilities (UARTBase)
├── uart_mac_reader.py      # MAC address reader
├── print_log.py             # Log printer with session logging
├── list_uart_devices.py    # Device lister
└── static/                  # Log files directory (auto-created)
```

## Development

### Install in Editable Mode

```bash
git clone https://github.com/375432636/uart-read-mac.git
cd uart-read-mac
pip install -e .
```

### Run Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/375432636/uart-read-mac/issues).
